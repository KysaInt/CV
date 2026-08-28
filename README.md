# CV

## 页面公共资源

作品页应按需引用以下公共文件，不要把对应样式或交互重新复制到页面内：

- `assets/css/site-theme.css`：全站渐变背景与滚动显隐状态。
- `assets/css/work-common.css`：作品页正文、标题和吸顶返回栏；已自动导入站点主题。
- `assets/css/gallery-common.css`：三列图片画廊与 16:9 顶部视频。
- `assets/css/video-common.css`：标准宽屏视频容器；特殊宽高比留在页面内覆盖。
- `assets/css/magazine-common.css`：图文混排缩略图。
- `assets/css/lightbox-common.css`：图片遮罩和动态图片放大层。
- `assets/css/media-overlay.css`：iframe/video 媒体遮罩。
- `assets/js/image-lightbox.js`：固定画廊图片预览，通过 `body[data-lightbox-selector]` 配置作用范围。
- `assets/js/zoom-modal.js`：`.zoomable-img` 图片放大。
- `assets/js/media-overlay.js`：媒体遮罩，通过 `body[data-media-overlay-selector]` 配置作用范围。
- `assets/js/sticky-title.js`、`scroll-animate.js`、`focus-work.js`：作品页标题、滚动动画和作品定位。
- `assets/js/resume-common.js`：简历页展开与返回滚动位置恢复。

页面内 `<style>` 只保留该页面独有的网格列数、媒体宽高比和项目布局。`guide.html` 与 `index2.html` 使用独立视觉主题，不应强制套用作品页样式。