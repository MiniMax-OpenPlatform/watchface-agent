"""
素材相关数据模型
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class AssetType(str, Enum):
    """素材类型枚举"""
    BACKGROUND_ROUND = "background_round"      # 圆形背景
    BACKGROUND_SQUARE = "background_square"    # 方形背景
    POINTER_HOUR = "pointer_hour"              # 时针
    POINTER_MINUTE = "pointer_minute"          # 分针
    POINTER_SECOND = "pointer_second"          # 秒针
    DIGIT_0 = "digit_0"                        # 数字0
    DIGIT_1 = "digit_1"                        # 数字1
    DIGIT_2 = "digit_2"                        # 数字2
    DIGIT_3 = "digit_3"                        # 数字3
    DIGIT_4 = "digit_4"                        # 数字4
    DIGIT_5 = "digit_5"                        # 数字5
    DIGIT_6 = "digit_6"                        # 数字6
    DIGIT_7 = "digit_7"                        # 数字7
    DIGIT_8 = "digit_8"                        # 数字8
    DIGIT_9 = "digit_9"                        # 数字9
    WEEK_MON = "week_mon"                      # 星期一
    WEEK_TUE = "week_tue"                      # 星期二
    WEEK_WED = "week_wed"                      # 星期三
    WEEK_THU = "week_thu"                      # 星期四
    WEEK_FRI = "week_fri"                      # 星期五
    WEEK_SAT = "week_sat"                      # 星期六
    WEEK_SUN = "week_sun"                      # 星期日
    PREVIEW = "preview"                        # 预览图
    DECORATION = "decoration"                  # 装饰元素


class AssetFile(BaseModel):
    """单个素材文件"""
    asset_type: AssetType
    filename: str                              # 原始文件名
    stored_filename: str                       # 存储文件名（规范化后）
    file_data: Optional[str] = None           # Base64数据（上传时使用）
    file_path: Optional[str] = None           # 文件路径（存储后）
    file_size: int = 0                        # 文件大小（字节）
    mime_type: str = "image/png"              # MIME类型
    
    @validator('filename')
    def validate_filename(cls, v):
        """验证文件名"""
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.webp']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f'不支持的文件格式，仅支持: {allowed_extensions}')
        return v


class WatchfaceAssets(BaseModel):
    """表盘素材集合"""
    background_round: Optional[AssetFile] = None
    background_square: Optional[AssetFile] = None
    
    # 指针模式素材
    pointer_hour: Optional[AssetFile] = None
    pointer_minute: Optional[AssetFile] = None
    pointer_second: Optional[AssetFile] = None
    
    # 数字模式素材（0-9）
    digits: List[AssetFile] = Field(default_factory=list)
    
    # 星期素材（MON-SUN）
    week_images: List[AssetFile] = Field(default_factory=list)
    
    # 装饰元素
    decorations: List[AssetFile] = Field(default_factory=list)
    
    # 预览图
    preview_image: Optional[AssetFile] = None
    
    def get_asset_by_type(self, asset_type: AssetType) -> Optional[AssetFile]:
        """根据类型获取素材"""
        mapping = {
            AssetType.BACKGROUND_ROUND: self.background_round,
            AssetType.BACKGROUND_SQUARE: self.background_square,
            AssetType.POINTER_HOUR: self.pointer_hour,
            AssetType.POINTER_MINUTE: self.pointer_minute,
            AssetType.POINTER_SECOND: self.pointer_second,
            AssetType.PREVIEW: self.preview_image,
        }
        return mapping.get(asset_type)
    
    def get_all_filenames(self) -> List[str]:
        """获取所有素材文件名"""
        filenames = []
        
        if self.background_round:
            filenames.append(self.background_round.stored_filename)
        if self.background_square:
            filenames.append(self.background_square.stored_filename)
        if self.pointer_hour:
            filenames.append(self.pointer_hour.stored_filename)
        if self.pointer_minute:
            filenames.append(self.pointer_minute.stored_filename)
        if self.pointer_second:
            filenames.append(self.pointer_second.stored_filename)
        
        for digit in self.digits:
            filenames.append(digit.stored_filename)
        
        for week in self.week_images:
            filenames.append(week.stored_filename)
        
        for decoration in self.decorations:
            filenames.append(decoration.stored_filename)
        
        if self.preview_image:
            filenames.append(self.preview_image.stored_filename)
        
        return filenames

