# intermediate-code-generator
[![CI](https://github.com/melonedo/intermediate-code-generator/actions/workflows/app.yaml/badge.svg)](https://github.com/melonedo/intermediate-code-generator/actions/workflows/app.yaml/)

2021 Compiler principles group design

## 运行测试
如果使用pipenv，则
```shell
pipenv install --dev
pipenv shell
pytest
```
如果需要卸载虚拟环境
```shell
pipenv --rm
```

另外也提供requirements.txt。

## LR分析表生成器
由于语法有歧义，生成器生成的语法需要手动编辑消除歧义。
```shell
git submodule update
pipenv shell
py intergen/tablegen.py
```
