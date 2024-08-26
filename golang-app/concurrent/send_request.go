// send concurrent request to mysql rds
// haimtran 26/08/2024

package concurrent

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"github.com/go-sql-driver/mysql"
)

const (
	USERNAME = "admin"
	PASSWORD = "Admin2024"
	DBNAME   = "demo"
	HOST     = "demo.ctgai60c2fpy.us-west-2.rds.amazonaws.com"
	PORT     = "3306"
  NUM_THREAD = 100
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

func GetEmployees() {

  fmt.Println("====================================")
	db, error := sql.Open("mysql", config.FormatDSN())

	if error != nil {
		log.Fatal("unable to use data source name", error)
	}

		// query employee table
		rows, error := db.Query("SELECT * FROM employees limit 1000")
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

    db.Close()
}

func SendConcurrentRequestToMySQL(){

  // create a channel
  ch := make(chan int)

  // send concurrent request to mysql rds
  for i := 0; i < NUM_THREAD; i++ {
    go func(i int) {
      fmt.Println("send concurrent request to mysql rds", i)

      GetEmployees()

      ch <- i;
    }(i)
  }

  // close channel wait for request processed
  for i := 0; i < NUM_THREAD; i++ {
    fmt.Println(<-ch)
  }
}



func SimpleLoadTestMySQL(){

  for {
    SendConcurrentRequestToMySQL()

    time.Sleep(10 * time.Second)
  }
}



func TestConcurrentByChannel() {
  // send concurrent request to mysql rds
  // ...

  ch := make(chan int)

  for i := 0; i < 10; i++ {
    go func(i int) {
      fmt.Println("send concurrent request to mysql rds", i)
      ch <- i; 
    }(i)
  }

  for i := 0; i < 10; i++ {
    fmt.Println(<-ch)
  }

}
