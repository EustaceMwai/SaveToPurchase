from SaveToPurchase import db
from SaveToPurchase.models import Base


Base.metadata.create_all(db.engine)
