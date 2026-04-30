/**
 * 抖音弹幕签名接口
 * 
 * 使用方式：
 * 1. 先加载 env.js（补充浏览器环境）
 * 2. 再加载 sign.js（包含 webmssdk 和 _0x5c2014 函数）
 * 3. 最后加载本文件（提供 get_sign 函数）
 * 4. 调用 get_sign(md5_value) 获取签名
 */
// 注意：在 execjs 环境中，不需要 require，直接按顺序加载即可
// require("./env.js")
// require("./sign.js")
// 签名函数 - 使用 window.byted_acrawler.frontierSign
function get_sign(md5_value) {
    // 优先使用 window.byted_acrawler.frontierSign
    let signFunc = null;
    
    if (typeof window !== 'undefined' && window.byted_acrawler && typeof window.byted_acrawler.frontierSign === 'function') {
        signFunc = window.byted_acrawler.frontierSign;
    } else if (typeof window !== 'undefined' && typeof window.yuan === 'function') {
        signFunc = window.yuan;
    } else if (typeof _0x5c2014 === 'function') {
        signFunc = _0x5c2014;
    } else {
        return "ERROR:SIGN_FUNCTION_NOT_FOUND";
    }
    
    try {
        // 尝试不同的调用方式
        let ret = null;
        
        // 方式1: 使用 X-MS-STUB 参数
        try {
            ret = signFunc({
                "X-MS-STUB": md5_value
            });
        } catch (e) {}
        
        // 方式2: 直接传入字符串
        if (!ret) {
            try {
                ret = signFunc(md5_value);
            } catch (e) {}
        }
        
        // 方式3: 使用空对象
        if (!ret) {
            try {
                ret = signFunc({});
            } catch (e) {}
        }
        
        // 尝试多种方式提取签名
        if (ret && typeof ret === 'object') {
            // 方式1: X-Bogus 字段
            if (ret["X-Bogus"]) {
                return ret["X-Bogus"];
            }
            // 方式2: signature 字段
            if (ret["signature"]) {
                return ret["signature"];
            }
            // 方式3: 返回整个对象的 JSON 字符串
            return JSON.stringify(ret);
        } else if (typeof ret === 'string') {
            return ret;
        } else {
            return "ERROR:UNEXPECTED_RETURN_TYPE";
        }
    } catch (e) {
        return "ERROR:" + e.message;
    }
}

// 导出到全局（供 execjs 直接调用）
if (typeof global !== 'undefined') {
    global.get_sign = get_sign;
}

// 导出函数供 Python execjs 调用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { get_sign };
    console.log("[danmu.js] ✓ get_sign 函数已导出");
}