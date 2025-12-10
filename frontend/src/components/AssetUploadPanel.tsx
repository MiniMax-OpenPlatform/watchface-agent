import React, { useState } from 'react';
import { Upload, Image as ImageIcon, Clock, Calendar, FileArchive, CheckCircle, X } from 'lucide-react';
import { uploadAsset, uploadBatchAssets, deleteAsset } from '../api/client';

interface AssetUploadPanelProps {
  sessionId: string;
  onAssetUploaded: (asset: any) => void;
  onAssetDeleted?: (assetType: string, filename: string) => void; // 新增：删除回调
  assets?: any; // 当前已上传的素材信息
}

const AssetUploadPanel: React.FC<AssetUploadPanelProps> = ({ sessionId, onAssetUploaded, onAssetDeleted, assets = {} }) => {
  const [uploading, setUploading] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleFileUpload = async (assetType: string, file: File) => {
    setUploading(assetType);
    try {
      const result = await uploadAsset(file, assetType, sessionId);
      onAssetUploaded(result.asset);
      alert(`✅ ${assetType} 上传成功！`);
    } catch (error: any) {
      alert(`❌ 上传失败: ${error.message}`);
    } finally {
      setUploading(null);
    }
  };

  const handleBatchUpload = async (assetCategory: string, file: File) => {
    setUploading(assetCategory);
    try {
      const result = await uploadBatchAssets(file, assetCategory, sessionId);
      // 批量上传返回多个素材，需要逐个通知
      if (result.assets && Array.isArray(result.assets)) {
        result.assets.forEach((asset: any) => onAssetUploaded(asset));
        alert(`✅ ${assetCategory} 批量上传成功！共上传 ${result.assets.length} 个文件`);
      }
    } catch (error: any) {
      alert(`❌ 批量上传失败: ${error.message}`);
    } finally {
      setUploading(null);
    }
  };

  const handleDeleteAsset = async (assetType: string, filename: string) => {
    if (!confirm('确定要删除这个素材吗？')) {
      return;
    }
    
    setDeleting(assetType);
    try {
      await deleteAsset(sessionId, filename);
      if (onAssetDeleted) {
        onAssetDeleted(assetType, filename);
      }
      alert(`✅ ${assetType} 删除成功！`);
    } catch (error: any) {
      alert(`❌ 删除失败: ${error.message}`);
    } finally {
      setDeleting(null);
    }
  };

  const FileUploader: React.FC<{ label: string; assetType: string; icon?: React.ReactNode }> = ({ label, assetType, icon }) => {
    // 获取已上传的素材信息
    const uploadedAsset = assets[assetType];
    const hasUploaded = uploadedAsset && uploadedAsset.stored_filename;
    
    return (
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-2">
          {icon}
          {label}
          {hasUploaded && (
            <span className="ml-auto flex items-center gap-1 text-xs text-green-600">
              <CheckCircle className="w-3 h-3" />
              已上传
            </span>
          )}
        </label>
        
        {/* 显示已上传的文件名 */}
        {hasUploaded && (
          <div className="mb-2 text-xs text-gray-600 bg-green-50 border border-green-200 rounded px-2 py-1 flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-green-600 flex-shrink-0" />
            <span className="truncate flex-1" title={uploadedAsset.original_filename}>
              {uploadedAsset.original_filename || uploadedAsset.stored_filename}
            </span>
            <button
              onClick={() => handleDeleteAsset(assetType, uploadedAsset.stored_filename)}
              disabled={deleting === assetType}
              className="ml-1 p-1 hover:bg-red-100 rounded-full text-red-600 transition-colors disabled:opacity-50"
              title="删除素材"
            >
              {deleting === assetType ? (
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-red-600"></div>
              ) : (
                <X className="w-3 h-3" />
              )}
            </button>
          </div>
        )}
        
        <div className="relative">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileUpload(assetType, file);
            }}
            disabled={uploading === assetType}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100
              disabled:opacity-50"
          />
          {uploading === assetType && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700"></div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="asset-upload-panel bg-white rounded-lg shadow p-6 overflow-y-auto">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <Upload className="w-5 h-5" />
        📤 素材上传
      </h3>

      {/* 背景图上传 */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 mb-3">表盘背景</h4>
        <FileUploader label="圆形背景" assetType="background_round" icon={<ImageIcon className="w-4 h-4" />} />
        <FileUploader label="方形背景" assetType="background_square" icon={<ImageIcon className="w-4 h-4" />} />
      </div>

      {/* 指针上传 */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 mb-3">指针素材</h4>
        <FileUploader label="时针" assetType="pointer_hour" icon={<Clock className="w-4 h-4" />} />
        <FileUploader label="分针" assetType="pointer_minute" icon={<Clock className="w-4 h-4" />} />
        <FileUploader label="秒针" assetType="pointer_second" icon={<Clock className="w-4 h-4" />} />
      </div>

      {/* 数字素材批量上传 */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <FileArchive className="w-4 h-4" />
          数字素材打包上传（0-9）
          {assets.digits && assets.digits.length > 0 && (
            <span className="ml-auto flex items-center gap-1 text-xs text-green-600">
              <CheckCircle className="w-3 h-3" />
              已上传 {assets.digits.length} 个
            </span>
          )}
        </h4>
        
        {/* 显示已上传的数字素材 */}
        {assets.digits && assets.digits.length > 0 && (
          <div className="mb-2 text-xs bg-green-50 border border-green-200 rounded p-2">
            <div className="flex flex-wrap gap-1">
              {assets.digits.map((digit: any, index: number) => (
                <span key={index} className="inline-flex items-center gap-1 bg-white px-2 py-0.5 rounded border border-green-300">
                  <CheckCircle className="w-3 h-3 text-green-600" />
                  {digit.original_filename || `digit_${index}`}
                </span>
              ))}
            </div>
          </div>
        )}
        
        <div className="bg-gray-50 p-3 rounded-md mb-2">
          <p className="text-xs text-gray-600 mb-1">💡 上传一个ZIP压缩包，包含10个数字图片：</p>
          <p className="text-xs text-gray-500">• 文件命名格式：<code className="bg-white px-1">digit_0.png</code>, <code className="bg-white px-1">digit_1.png</code>, ..., <code className="bg-white px-1">digit_9.png</code></p>
          <p className="text-xs text-gray-500">• 系统会自动识别文件名并分类</p>
        </div>
        <div className="relative">
          <input
            type="file"
            accept=".zip"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleBatchUpload('digits', file);
            }}
            disabled={uploading === 'digits'}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-purple-50 file:text-purple-700
              hover:file:bg-purple-100
              disabled:opacity-50"
          />
          {uploading === 'digits' && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-700"></div>
            </div>
          )}
        </div>
      </div>

      {/* 星期素材批量上传 */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <FileArchive className="w-4 h-4" />
          星期素材打包上传（周一至周日）
          {assets.week_images && assets.week_images.length > 0 && (
            <span className="ml-auto flex items-center gap-1 text-xs text-green-600">
              <CheckCircle className="w-3 h-3" />
              已上传 {assets.week_images.length} 个
            </span>
          )}
        </h4>
        
        {/* 显示已上传的星期素材 */}
        {assets.week_images && assets.week_images.length > 0 && (
          <div className="mb-2 text-xs bg-green-50 border border-green-200 rounded p-2">
            <div className="flex flex-wrap gap-1">
              {assets.week_images.map((week: any, index: number) => (
                <span key={index} className="inline-flex items-center gap-1 bg-white px-2 py-0.5 rounded border border-green-300">
                  <CheckCircle className="w-3 h-3 text-green-600" />
                  {week.original_filename || `week_${index + 1}`}
                </span>
              ))}
            </div>
          </div>
        )}
        
        <div className="bg-gray-50 p-3 rounded-md mb-2">
          <p className="text-xs text-gray-600 mb-1">💡 上传一个ZIP压缩包，包含7个星期图片：</p>
          <p className="text-xs text-gray-500">• 文件命名格式：<code className="bg-white px-1">week_1.png</code>, <code className="bg-white px-1">week_2.png</code>, ..., <code className="bg-white px-1">week_7.png</code></p>
          <p className="text-xs text-gray-500">• week_1=周一, week_2=周二, ..., week_7=周日</p>
        </div>
        <div className="relative">
          <input
            type="file"
            accept=".zip"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleBatchUpload('week_images', file);
            }}
            disabled={uploading === 'week_images'}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-green-50 file:text-green-700
              hover:file:bg-green-100
              disabled:opacity-50"
          />
          {uploading === 'week_images' && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-700"></div>
            </div>
          )}
        </div>
      </div>

      {/* 预览图上传 */}
      <div className="mb-4" style={{ display: 'none' }}>
        <h4 className="font-semibold text-gray-800 mb-3">预览图</h4>
        <FileUploader label="表盘预览图" assetType="preview" icon={<ImageIcon className="w-4 h-4" />} />
      </div>

      <div className="text-xs text-gray-500 mt-4" style={{ display: 'none' }}>
        <p>💡 支持格式：PNG, JPG, JPEG, WebP</p>
        <p>💡 建议尺寸：466x466（圆形）/ 480x480（方形）</p>
      </div>
    </div>
  );
};

export default AssetUploadPanel;

