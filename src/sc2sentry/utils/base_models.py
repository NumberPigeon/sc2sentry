from pydantic import BaseModel


# 使用自定义的 BaseModel 代替 pydantic.BaseModel，
# 这样允许我们自定义整个项目的 Model 的行为，如控制时间戳的格式
class BaseModel(BaseModel):
    pass
