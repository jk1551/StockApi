from pydantic import BaseModel  #,constr

# Defines Various Schemas (JSON as calsses) for accepting request and returning response


class readStockList(BaseModel):
  name: str


class updateStockList(BaseModel):
  name: str

class removeSingleFromStockList(BaseModel):
  name: str
