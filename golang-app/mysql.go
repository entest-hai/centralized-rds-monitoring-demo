// connect to rds mysql
// haimtran 24/08/2024
package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/go-sql-driver/mysql"
)

const (
	USERNAME = ""
	PASSWORD = ""
	DBNAME   = ""
	HOST     = ""
	PORT     = "3306"
)

type Employee struct {
	ID   int
	Name string
	Age  int
	Time string
}

var config mysql.Config = mysql.Config{
	User:                 USERNAME,
	Passwd:               PASSWORD,
	Net:                  "tcp",
	Addr:                 fmt.Sprintf("%s:%s", HOST, PORT),
	DBName:               DBNAME,
	AllowNativePasswords: true,
}

func loadTestMySQL() {
	db, error := sql.Open("mysql", config.FormatDSN())

	if error != nil {
		log.Fatal("unable to use data source name", error)
	}

	// error = db.Ping()
	var count int = 0
	for true {
		fmt.Println(fmt.Sprintf("iteration %d", count), "===========================")
		// query employee table
		rows, error := db.Query("SELECT * FROM employees limit 10")
		if error != nil {
			log.Fatal("unable to execute query", error)
		}

		// parse the returned rows
		for rows.Next() {
			var employee Employee
			error := rows.Scan(&employee.ID, &employee.Name, &employee.Age, &employee.Time)
			if error != nil {
				log.Fatal("unable to scan row", error)
			}
			fmt.Println(employee)
		}
		// sleep for 5 seconds
		time.Sleep(2 * time.Second)
		count = count + 1

	}

}

func getEmployees() []byte {

	// employee
	var employee Employee
	var employees []Employee

	// create a db connection
	db, error := sql.Open("mysql", config.FormatDSN())

	if error != nil {
		log.Fatal("unable to use data source name", error)
	}

  // query employees 
	rows, error := db.Query("SELECT * FROM employees limit 100")
	if error != nil {
		log.Fatal("unable to execute query", error)
	}

	// parse the returned rows
	for rows.Next() {
		error := rows.Scan(&employee.ID, &employee.Name, &employee.Age, &employee.Time)
		if error != nil {
			log.Fatal("unable to scan row", error)
		}
		employees = append(employees, employee)
	}

	// convert to bytes
	bytes, error := json.Marshal(employees)

	if error != nil {
		log.Fatal(error)
	}

	return bytes
}

func TestMySQLWebServer() {

	mux := http.NewServeMux()

	mux.HandleFunc("/json", func(w http.ResponseWriter, r *http.Request) {
		data := getEmployees()
		w.Header().Set("Content-Type", "application/json")
		w.Write(data)
	})

	server := &http.Server{
		Addr:           ":3000",
		Handler:        mux,
		ReadTimeout:    10 * time.Second,
		WriteTimeout:   10 * time.Second,
		MaxHeaderBytes: 1 << 20,
	}

	log.Fatal(server.ListenAndServe())

}
