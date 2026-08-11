from app.models.drive import PlacementDriveInDB
from app.repositories.base import BaseRepository


class PlacementDriveRepository(BaseRepository[PlacementDriveInDB]):
    collection_name = "placement_drives"
    model = PlacementDriveInDB
