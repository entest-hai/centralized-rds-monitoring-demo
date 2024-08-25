---
title: connect to mysql on aws
author: haimtran
date: 24/08/2024
---

## Setup Ubuntu

Install mysql client.

```bash
sudo apt-get install mysql-client
```

## Setup Amazon Linux

Install this LAMP stack.

```bash
sudo dnf update -y
sudo dnf install -y httpd wget php-fpm php-mysqli php-json php php-devel
sudo dnf install mariadb105-server
```

Check mysql client version.

```bash
mysql --version
```

## Connect MySQL

```bash
sudo mysql -h demo.ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p
```

Show databses and tables.

```sql
show databases;
show tables;
use demo;
```

Create a book table.

```sql
CREATE TABLE IF NOT EXISTS book (
    id int auto_increment primary key,
    author text,
    title text,
    amazon text,
    image text);
```

Insert some records.

```sql
INSERT INTO book(author, title, amazon, image) VALUES ('Hai Tran', 'Deep Learning', '', 'hello.jpg');
```

## Golang MySQL

## Python MySQL

## Connect PostgreSQL

```bash
psql -h database-2.cluster-c7qmawum6auz.ap-southeast-1.rds.amazonaws.com -p 5432 -U postgres -d demo
```

Show databases and tables.

```sql
\dt
```

Create a book table.

```sql
CREATE TABLE IF NOT EXISTS book (
    id int auto_increment primary key,
    author text,
    title text,
    amazon text,
    image text);
```

Insert some records.

```sql
INSERT INTO book(author, title, amazon, image) VALUES ('Hai Tran', 'Deep Learning', '', 'hello.jpg');
```
