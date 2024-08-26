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
sudo mysql -h database-cluster.cluster-ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p
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
psql -h database-cluster.cluster-ctgai60c2fpy.us-west-2.rds.amazonaws.com -p 5432 -U postgres -d demo
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

## Load Sample Data

Clone [test_db git repository](https://github.com/datacharmer/test_db).

Load sakila sample data.

```bash
sudo mysql -h demo.ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo < sakila-mv-schema.sql
sudo mysql -h aurora-cluster.cluster-ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo < sakila-mv-data.sql
sudo mysql -h demo.ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo < sakila-mv-schema.sql
```

RDS Multi-AZ cluster MySQL, writer endpoint.

```bash
sudo mysql -h database-cluster.cluster-ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p mysql
sudo mysql -h database-cluster.cluster-ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo < sakila-mv-schema.sql
sudo mysql -h database-cluster.cluster-ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo < sakila-mv-data.sql
```

RDS Aurora MySQL.

```bash
sudo mysql -h aurora-cluster-instance-1.ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo
sudo mysql -h aurora-cluster-instance-1.ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo < sakila-mv-schema.sql
sudo mysql -h aurora-cluster-instance-1.ctgai60c2fpy.us-west-2.rds.amazonaws.com -P 3306 -u admin -p demo < sakila-mv-data.sql
```

Load employees data.

```bash
sudo mysql -h <DB_HOST> -P 3306 -u admin -p demo < employees.sql
```

## Troubleshooting

Enable log_bin_trust_function_creators from parameter_group.

```bash
mysql -u USERNAME -p
set global log_bin_trust_function_creators=1;
```

Modify the ENGINE in sql.

```sql
CREATE TABLE film_text (
  film_id SMALLINT NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  PRIMARY KEY  (film_id),
  FULLTEXT KEY idx_title_description (title,description)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

Increase max-allowed-packet in parameter_group for aurora

```bash
max-allowed-packet
```

Show the original values of a parameter.

```bash
SHOW GLOBAL VARIABLES where Variable_Name='innodb_buffer_pool_size';
SHOW GLOBAL VARIABLES where Variable_Name='max-allowed-packet';
```

## Reference

- [Amazon Aurora MySQL Database Configuration](https://aws.amazon.com/blogs/database/best-practices-for-amazon-aurora-mysql-database-configuration/)
