# LAIN CLI

[![MIT license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)

CLI 是用户使用 LAIN 平台的入口工具。用户对自己应用的部署，升级，查看等操作都要通过 CLI。

CLI 相关命令文档可以在 [LAIN White Paper](https://laincloud.gitbooks.io/white-paper/content/usermanual/sdkandcli.html) 中查看。

## 安装

```
pip install lain-cli
```

## 打包上传到 PyPI

### 依赖

```
pip install twine  # 上传工具
pip install wheel  # 打包工具
```

### 打包上传

```
rm -rf dist/  # 清空以前的构建
python setup.py sdist  # 打包源代码
python setup.py bdist_wheel  # 构建 wheel
twine upload dist/*  # 上传
```
