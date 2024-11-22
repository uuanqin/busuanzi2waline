# 不蒜子数据导出脚本

本脚本的主要功能有：
- 根据提供的 sitemap 将不蒜子中存储的数据导出为 JSON 格式
- 支持通过从不蒜子导出的数据生成对应的 SQL 语句，以将数据更新到 Waline 中

可调整的参数（详看 [本小节](#选项说明)）：
- 线程启动的间隔时间
- 请求失败重试次数

更多信息详见我的博客文章：https://blog.uuanqin.top/p/e400f664/

## 简介

### 不蒜子

[不蒜子](https://busuanzi.ibruce.info/) 是一个免费的静态网站访问量统计服务，支持多种显示效果和自定义选项，可直接在网页上显示访问次数。

但是对于个人开发者而言，不蒜子中的统计数据难以维护：
- 对于上线一段时间的网站，初始化的统计量需要联系开发者修改
- 当域名更换时不蒜子中的数据清零

### Waline 评论系统

[Waline](https://waline.js.org/) 是一款从 Valine 衍生的带后端评论系统。除了常规的评论功能外，还支持统计页面浏览量。

## 快速开始

只需以下三个步骤：

1. 克隆本仓库 `sql_generator.py`。

```shell
git clone git@github.com:uuanqin/busuanzi2waline.git
```

2. 修改 `sitemap.txt` 文件，在里面填写需要导出数据的网址，一行一个网址。

```text
https://blog.uuanqin.top/p/d4bc55f2/
https://blog.uuanqin.top/p/e1ee5eca/
```

3. 运行脚本。

```shell
python sql_generator.py -gu 
```

`out_add_json` 文件中的数据即为导出的数据。

```json
[
  {
    "site_uv": 419,
    "page_pv": 2,
    "version": 2.4,
    "site_pv": 434,
    "url": "/p/d4bc55f2/"
  },
  {
    "site_uv": 420,
    "page_pv": 2,
    "version": 2.4,
    "site_pv": 435,
    "url": "/p/e1ee5eca/"
  }
]
```

其中：
- `page_pv` 表示对应路径 `url` 下的页面浏览量
- `site_pv` 表示网站 https://blog.uuanqin.top 的页面浏览量
- `site_pv` 表示网站 https://blog.uuanqin.top 的独立访客数

> [!NOTE] 
> 脚本每次发出请求时，不蒜子会正常统计访问次数

如果部分地址请求失败，失败网址将记录在 `out_add_fail.json` 中。

## 将数据迁移至 Waline

Waline 客户端在开启 [pageview](https://waline.js.org/guide/features/pageview.html) 
选项时，页面统计量将记入数据库中 `wl_Counter` 表的 time 字段中。

但是 `wl_Counter` 中并不一定包含对应着所有网页的记录，为了后续的数据迁移方便，我们可以利用脚本为
没在 `wl_Counter` 中的网址添加一条初始记录。

```shell
python sql_generator.py -gi
```

得到文件 `out_ins.sql`。

```sql
INSERT INTO wl_Counter (url, time) SELECT '/p/d4bc55f2/', 0 WHERE NOT EXISTS (SELECT 1 FROM wl_Counter WHERE url = '/p/d4bc55f2/');
INSERT INTO wl_Counter (url, time) SELECT '/p/e1ee5eca/', 0 WHERE NOT EXISTS (SELECT 1 FROM wl_Counter WHERE url = '/p/e1ee5eca/');
```

在 [快速开始](#快速开始) 这一小节中，除了 `out_add.json` 生成之外，还额外生成了 `out_add.sql`，
在数据库中执行这些更新语句，可以在 Waline 原有数据的基础上，**增加** 从不蒜子中获取的数据。

```sql
UPDATE wl_Counter SET time = IFNULL(time, 0) + 2 WHERE url = '/p/d4bc55f2/';
UPDATE wl_Counter SET time = IFNULL(time, 0) + 2 WHERE url = '/p/e1ee5eca/';
```

## 选项说明

脚本完整使用的方式如下：

```shell
python sql_generator.py -gi -gu -de 1 -r 2 -v
```

`-gi`、`--gen_ins` 选项指定脚本根据 sitemap.txt 生成相应 SQL，插入 Waline 数据库中不存在对应网址的记录，以为后面的数据导入做准备

`-gu`、`--gen_upd` 选项指定脚本根据 sitemap.txt 获取不蒜子中的数据，并生成相应 SQL 更新 Waline 数据库

`-r`、`--retry` 指定请求失败时的重试次数，默认 3 次。每次重试都会随机延迟更久的时间。

`-de`、`--delay` 指定每个线程延时时间，随机延时 0.5 ~ n 秒。

`-v`、`--verbose` 调试用，输出详尽的处理信息。

## 许可证

MIT
