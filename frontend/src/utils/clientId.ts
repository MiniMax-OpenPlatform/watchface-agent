/**
 * 客户端ID管理工具
 * 用于生成和管理唯一的浏览器标识
 */

const CLIENT_ID_KEY = 'watchface_client_id';

/**
 * 生成简单的浏览器指纹
 * 基于浏览器特征生成唯一标识
 */
function generateBrowserFingerprint(): string {
  const nav = window.navigator;
  const screen = window.screen;
  
  const features = [
    nav.userAgent,
    nav.language,
    screen.colorDepth,
    screen.width,
    screen.height,
    new Date().getTimezoneOffset(),
    !!window.sessionStorage,
    !!window.localStorage,
  ];
  
  // 生成简单的hash
  const fingerprint = features.join('|');
  return btoa(fingerprint).replace(/[^a-zA-Z0-9]/g, '').substring(0, 32);
}

/**
 * 生成随机的客户端ID
 */
function generateRandomId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 15);
  const fingerprint = generateBrowserFingerprint();
  
  return `${timestamp}-${random}-${fingerprint}`;
}

/**
 * 获取或创建客户端ID
 */
export function getClientId(): string {
  try {
    // 尝试从localStorage获取
    let clientId = localStorage.getItem(CLIENT_ID_KEY);
    
    if (!clientId) {
      // 如果不存在，生成新的
      clientId = generateRandomId();
      localStorage.setItem(CLIENT_ID_KEY, clientId);
      console.log('🆔 生成新的客户端ID:', clientId);
    } else {
      console.log('🆔 使用已存在的客户端ID:', clientId);
    }
    
    return clientId;
  } catch (error) {
    console.error('❌ 获取客户端ID失败:', error);
    // 降级方案：使用临时ID
    return `temp-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
  }
}

/**
 * 重置客户端ID（用于调试）
 */
export function resetClientId(): string {
  try {
    localStorage.removeItem(CLIENT_ID_KEY);
    return getClientId();
  } catch (error) {
    console.error('❌ 重置客户端ID失败:', error);
    return getClientId();
  }
}

/**
 * 获取客户端信息（用于调试）
 */
export function getClientInfo() {
  const clientId = getClientId();
  const nav = window.navigator;
  
  return {
    clientId,
    userAgent: nav.userAgent,
    language: nav.language,
    platform: nav.platform,
    screenResolution: `${window.screen.width}x${window.screen.height}`,
  };
}

