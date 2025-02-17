# harmoe图片下载器

这是一个用于从harmoe FC网站（ https://harmoe-fc.jp ） 下载图片的Python脚本。

## 功能描述

该程序允许用户：

1. 登录harmoe FC网站
2. 指定日期范围
3. 自动下载指定日期范围内的所有图片

## 主要特性

- 使用图形用户界面(GUI)进行交互
- 支持日期范围选择
- 多线程下载，提高效率
- 详细的日志记录
- 错误处理和用户友好的提示

## 使用方法

1. 运行脚本
2. 输入FC登录ID和密码
3. 指定开始和结束日期（格式：YYYYMMDD）
4. 选择下载路径
5. 等待下载完成

## 依赖库

- requests
- BeautifulSoup4
- tkinter

## 注意事项

- 请确保您有权访问和下载这些图片（即拥有fc正式会员账号）
- 下载大量图片可能需要较长时间，请耐心等待
- 如遇到问题，请查看`download_log.txt`日志文件

## 免责声明

本程序仅用于学习和研究目的。使用者应遵守相关网站的使用条款和版权规定。
