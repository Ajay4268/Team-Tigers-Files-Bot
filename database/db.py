import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

logger = logging.getLogger(__name__)

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    async def connect(self):
        if self._initialized:
            return
        self.client  = AsyncIOMotorClient(Config.MONGO_URI)
        self.db      = self.client[Config.DB_NAME]
        self.files   = self.db["files"]
        self.users   = self.db["users"]
        self.premium = self.db["premium"]

        await self.files.create_index([("file_name", "text"), ("caption", "text")])
        await self.files.create_index("file_id", unique=True)
        await self.premium.create_index("user_id", unique=True)
        self._initialized = True
        logger.info("MongoDB indexes ensured.")

    # ── File Operations ──────────────────────────────────────────

    async def save_file(self, file_data: dict) -> bool:
        try:
            await self.files.insert_one(file_data)
            return True
        except Exception:
            return False

    async def search_files(self, query: str, max_results: int = 10) -> list:
        results = []
        cursor = self.files.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(max_results)
        async for doc in cursor:
            results.append(doc)
        if not results:
            regex_cursor = self.files.find(
                {"file_name": {"$regex": query, "$options": "i"}}
            ).limit(max_results)
            async for doc in regex_cursor:
                results.append(doc)
        return results

    async def get_file_by_id(self, file_unique_id: str) -> dict | None:
        return await self.files.find_one({"file_unique_id": file_unique_id})

    async def total_files(self) -> int:
        return await self.files.count_documents({})

    async def delete_file(self, file_unique_id: str) -> bool:
        result = await self.files.delete_one({"file_unique_id": file_unique_id})
        return result.deleted_count > 0

    # ── User Operations ──────────────────────────────────────────

    async def add_user(self, user_id: int):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )

    async def total_users(self) -> int:
        return await self.users.count_documents({})

    # ── Premium Operations ────────────────────────────────────────

    async def add_premium(self, user_id: int, plan: str) -> dict:
        """Grant premium to user. Returns the premium doc."""
        days = Config.PREMIUM_PLANS[plan]["days"]
        now  = datetime.utcnow()

        # If already premium, extend from current expiry
        existing = await self.premium.find_one({"user_id": user_id})
        if existing and existing["expires_at"] > now:
            start = existing["expires_at"]
        else:
            start = now

        expires_at = start + timedelta(days=days)

        doc = {
            "user_id"   : user_id,
            "plan"      : plan,
            "granted_at": now,
            "expires_at": expires_at,
            "active"    : True,
        }
        await self.premium.update_one(
            {"user_id": user_id},
            {"$set": doc},
            upsert=True
        )
        return doc

    async def remove_premium(self, user_id: int):
        await self.premium.delete_one({"user_id": user_id})

    async def is_premium(self, user_id: int) -> bool:
        """Return True if user has an active, non-expired premium subscription."""
        if user_id in Config.ADMINS:
            return True   # Admins always have premium
        doc = await self.premium.find_one({"user_id": user_id})
        if not doc:
            return False
        return doc["expires_at"] > datetime.utcnow()

    async def get_premium_info(self, user_id: int) -> dict | None:
        doc = await self.premium.find_one({"user_id": user_id})
        if doc and doc["expires_at"] > datetime.utcnow():
            return doc
        return None

    async def total_premium_users(self) -> int:
        now = datetime.utcnow()
        return await self.premium.count_documents({"expires_at": {"$gt": now}})

    async def get_all_premium(self) -> list:
        now = datetime.utcnow()
        cursor = self.premium.find({"expires_at": {"$gt": now}})
        return [doc async for doc in cursor]

    # ── Pending Payment Requests ──────────────────────────────────

    async def create_payment_request(self, user_id: int, plan: str) -> str:
        """Store a pending payment request and return a request ID."""
        import uuid
        req_id = str(uuid.uuid4())[:8].upper()
        await self.db["payments"].insert_one({
            "req_id"    : req_id,
            "user_id"   : user_id,
            "plan"      : plan,
            "status"    : "pending",
            "created_at": datetime.utcnow(),
        })
        return req_id

    async def get_payment_request(self, req_id: str) -> dict | None:
        return await self.db["payments"].find_one({"req_id": req_id})

    async def approve_payment(self, req_id: str) -> dict | None:
        req = await self.get_payment_request(req_id)
        if not req:
            return None
        await self.db["payments"].update_one(
            {"req_id": req_id}, {"$set": {"status": "approved"}}
        )
        return await self.add_premium(req["user_id"], req["plan"])

    async def list_pending_payments(self) -> list:
        cursor = self.db["payments"].find({"status": "pending"}).sort("created_at", 1)
        return [doc async for doc in cursor]
