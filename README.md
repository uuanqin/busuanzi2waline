# ���������ݵ����ű�

���ű�����Ҫ�����У�
- �����ṩ�� sitemap ���������д洢�����ݵ���Ϊ JSON ��ʽ
- ֧��ͨ���Ӳ����ӵ������������ɶ�Ӧ�� SQL ��䣬�Խ����ݸ��µ� Waline ��

�ɵ����Ĳ������꿴 [��С��](#ѡ��˵��)����
- �߳������ļ��ʱ��
- ����ʧ�����Դ���

������Ϣ����ҵĲ������£�https://blog.uuanqin.top/p/e400f664/

## ���

### ������

[������](https://busuanzi.ibruce.info/) ��һ����ѵľ�̬��վ������ͳ�Ʒ���֧�ֶ�����ʾЧ�����Զ���ѡ���ֱ������ҳ����ʾ���ʴ�����

���Ƕ��ڸ��˿����߶��ԣ��������е�ͳ����������ά����
- ��������һ��ʱ�����վ����ʼ����ͳ������Ҫ��ϵ�������޸�
- ����������ʱ�������е���������

### Waline ����ϵͳ

[Waline](https://waline.js.org/) ��һ��� Valine �����Ĵ��������ϵͳ�����˳�������۹����⣬��֧��ͳ��ҳ���������

## ���ٿ�ʼ

ֻ�������������裺

1. ��¡���ֿ� `sql_generator.py`��

```shell
git clone git@github.com:uuanqin/busuanzi2waline.git
```

2. �޸� `sitemap.txt` �ļ�����������д��Ҫ�������ݵ���ַ��һ��һ����ַ��

```text
https://blog.uuanqin.top/p/d4bc55f2/
https://blog.uuanqin.top/p/e1ee5eca/
```

3. ���нű���

```shell
python sql_generator.py -gu 
```

`out_add_json` �ļ��е����ݼ�Ϊ���������ݡ�

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

���У�
- `page_pv` ��ʾ��Ӧ·�� `url` �µ�ҳ�������
- `site_pv` ��ʾ��վ https://blog.uuanqin.top ��ҳ�������
- `site_pv` ��ʾ��վ https://blog.uuanqin.top �Ķ����ÿ���

> [!NOTE] 
> �ű�ÿ�η�������ʱ�������ӻ�����ͳ�Ʒ��ʴ���

������ֵ�ַ����ʧ�ܣ�ʧ����ַ����¼�� `out_add_fail.json` �С�

## ������Ǩ���� Waline

Waline �ͻ����ڿ��� [pageview](https://waline.js.org/guide/features/pageview.html) 
ѡ��ʱ��ҳ��ͳ�������������ݿ��� `wl_Counter` ��� time �ֶ��С�

���� `wl_Counter` �в���һ��������Ӧ��������ҳ�ļ�¼��Ϊ�˺���������Ǩ�Ʒ��㣬���ǿ������ýű�Ϊ
û�� `wl_Counter` �е���ַ���һ����ʼ��¼��

```shell
python sql_generator.py -gi
```

�õ��ļ� `out_ins.sql`��

```sql
INSERT INTO wl_Counter (url, time) SELECT '/p/d4bc55f2/', 0 WHERE NOT EXISTS (SELECT 1 FROM wl_Counter WHERE url = '/p/d4bc55f2/');
INSERT INTO wl_Counter (url, time) SELECT '/p/e1ee5eca/', 0 WHERE NOT EXISTS (SELECT 1 FROM wl_Counter WHERE url = '/p/e1ee5eca/');
```

�� [���ٿ�ʼ](#���ٿ�ʼ) ��һС���У����� `out_add.json` ����֮�⣬������������ `out_add.sql`��
�����ݿ���ִ����Щ������䣬������ Waline ԭ�����ݵĻ����ϣ�**����** �Ӳ������л�ȡ�����ݡ�

```sql
UPDATE wl_Counter SET time = IFNULL(time, 0) + 2 WHERE url = '/p/d4bc55f2/';
UPDATE wl_Counter SET time = IFNULL(time, 0) + 2 WHERE url = '/p/e1ee5eca/';
```

## ѡ��˵��

�ű�����ʹ�õķ�ʽ���£�

```shell
python sql_generator.py -gi -gu -de 1 -r 2 -v
```

`-gi`��`--gen_ins` ѡ��ָ���ű����� sitemap.txt ������Ӧ SQL������ Waline ���ݿ��в����ڶ�Ӧ��ַ�ļ�¼����Ϊ��������ݵ�����׼��

`-gu`��`--gen_upd` ѡ��ָ���ű����� sitemap.txt ��ȡ�������е����ݣ���������Ӧ SQL ���� Waline ���ݿ�

`-r`��`--retry` ָ������ʧ��ʱ�����Դ�����Ĭ�� 3 �Ρ�ÿ�����Զ�������ӳٸ��õ�ʱ�䡣

`-de`��`--delay` ָ��ÿ���߳���ʱʱ�䣬�����ʱ 0.5 ~ n �롣

`-v`��`--verbose` �����ã�����꾡�Ĵ�����Ϣ��

## ���֤

MIT
