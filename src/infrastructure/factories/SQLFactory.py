class SQLiteFactory:
    def __init__(
        self,
        library_db: str = "library.db",
        listening_db: str = "listening.db"
    ):
        self._library_db = SQLiteDatabaseManager(library_db)
        self._listening_db = SQLiteDatabaseManager(listening_db)
    
    def repo_bundle(self) -> SQLiteRepoBundle:
        return SQLiteRepoBundle(self._library_db)
    
    def persistence(self) -> SQLitePersistenceAdapter:
        return SQLitePersistenceAdapter(self._library_db)
    
    def tracking(self) -> SQLiteTrackingAdapter:
        return SQLiteTrackingAdapter(self._listening_db)