package main

import (
	"encoding/json"
	"fmt"
	"os"

	"math/rand"
	"net/http"
	"time"

	log "github.com/sirupsen/logrus"
)

const (
	// Host name of the HTTP Server
	Host = "0.0.0.0"
	// Port of the HTTP Server
	Port = "8080"
)

// Dog has a name and a gender
type Dog struct {
	Name   string
	Gender string
}

var femaleNames = []string{
	"Abby", "Addie", "Alexis", "Alice", "Allie", "Alyssa", "Amber", "Angel", "Anna",
	"Annie", "Ariel", "Ashley", "Aspen", "Athena", "Autumn", "Ava", "Avery", "Baby",
	"Bailey", "Basil", "Bean", "Bella", "Belle", "Betsy", "Betty", "Bianca", "Birdie",
	"Biscuit", "Blondie", "Blossom", "Bonnie", "Brandy", "Brooklyn", "Brownie", "Buffy",
	"Callie", "Camilla", "Candy", "Carla", "Carly", "Carmela", "Casey", "Cassie", "Chance",
	"Chanel", "Chloe", "Cinnamon", "Cleo", "Coco", "Cookie", "Cricket", "Daisy", "Dakota",
	"Dana", "Daphne", "Darla", "Darlene", "Delia", "Delilah", "Destiny", "Diamond", "Diva",
	"Dixie", "Dolly", "Duchess", "Eden", "Edie", "Ella", "Ellie", "Elsa", "Emma", "Emmy",
	"Eva", "Faith", "Fanny", "Fern", "Fiona", "Foxy", "Gabby", "Gemma", "Georgia", "Gia",
	"Gidget", "Gigi", "Ginger", "Goldie", "Grace", "Gracie", "Greta", "Gypsy", "Hailey",
	"Hannah", "Harley", "Harper", "Hazel", "Heidi", "Hershey", "Holly", "Honey", "Hope",
	"Ibby", "Inez", "Isabella", "Ivy", "Izzy", "Jackie", "Jada", "Jade", "Jasmine", "Jenna",
	"Jersey", "Jessie", "Jill", "Josie", "Julia", "Juliet", "Juno", "Kali", "Kallie", "Karma",
	"Kate", "Katie", "Kayla", "Kelsey", "Khloe", "Kiki", "Kira", "Koko", "Kona", "Lacy", "Lady",
	"Layla", "Leia", "Lena", "Lexi", "Libby", "Liberty", "Lily", "Lizzy", "Lola", "London",
	"Lucky", "Lulu", "Luna", "Mabel", "Mackenzie", "Macy", "Maddie", "Madison", "Maggie",
	"Maisy", "Mandy", "Marley", "Matilda", "Mattie", "Maya", "Mia", "Mika", "Mila", "Miley",
	"Millie", "Mimi", "Minnie", "Missy", "Misty", "Mitzi", "Mocha", "Molly", "Morgan", "Moxie",
	"Muffin", "Mya", "Nala", "Nell", "Nellie", "Nikki", "Nina", "Noel", "Nola", "Nori", "Olive",
	"Olivia", "Oreo", "Paisley", "Pandora", "Paris", "Peaches", "Peanut", "Pearl", "Pebbles",
	"Penny", "Pepper", "Phoebe", "Piper", "Pippa", "Pixie", "Polly", "Poppy", "Precious",
	"Princess", "Priscilla", "Raven", "Reese", "Riley", "Rose", "Rosie", "Roxy", "Ruby", "Sadie",
	"Sage", "Sally", "Sam", "Samantha", "Sammie", "Sandy", "Sasha", "Sassy", "Savannah",
	"Scarlet", "Shadow", "Sheba", "Shelby", "Shiloh", "Sierra", "Sissy", "Sky", "Smokey",
	"Snickers", "Sophia", "Sophie", "Star", "Stella", "Sugar", "Suki", "Summer", "Sunny",
	"Sweetie", "Sydney", "Tasha", "Tessa", "Tilly", "Tootsie", "Trixie", "Violet", "Willow",
	"Winnie", "Xena", "Zelda", "Zoe",
}

var maleNames = []string{
	"Abe", "Abbott", "Ace", "Aero", "Aiden", "AJ", "Albert", "Alden", "Alex", "Alfie", "Alvin",
	"Amos", "Andy", "Angus", "Apollo", "Archie", "Aries", "Artie", "Ash", "Austin", "Axel",
	"Bailey", "Bandit", "Barkley", "Barney", "Baron", "Baxter", "Bear", "Beau", "Benji",
	"Benny", "Bentley", "Billy", "Bingo", "Blake", "Blaze", "Blue", "Bo", "Boomer", "Brady",
	"Brody", "Brownie", "Bruce", "Bruno", "Brutus", "Bubba", "Buck", "Buddy", "Buster", "Butch",
	"Buzz", "Cain", "Captain", "Carter", "Cash", "Casper", "Champ", "Chance", "Charlie",
	"Chase", "Chester", "Chewy", "Chico", "Chief", "Chip", "CJ", "Clifford", "Clyde", "Coco",
	"Cody", "Colby", "Cooper", "Copper", "Damien", "Dane", "Dante", "Denver", "Dexter", "Diego",
	"Diesel", "Dodge", "Drew", "Duke", "Dylan", "Eddie", "Eli", "Elmer", "Emmett", "Evan",
	"Felix", "Finn", "Fisher", "Flash", "Frankie", "Freddy", "Fritz", "Gage", "George", "Gizmo",
	"Goose", "Gordie", "Griffin", "Gunner", "Gus", "Hank", "Harley", "Harvey", "Hawkeye",
	"Henry", "Hoss", "Huck", "Hunter", "Iggy", "Ivan", "Jack", "Jackson", "Jake", "Jasper",
	"Jax", "Jesse", "Joey", "Johnny", "Judge", "Kane", "King", "Kobe", "Koda", "Lenny", "Leo",
	"Leroy", "Levi", "Lewis", "Logan", "Loki", "Louie", "Lucky", "Luke", "Marley", "Marty",
	"Maverick", "Max", "Maximus", "Mickey", "Miles", "Milo", "Moe", "Moose", "Morris", "Murphy",
	"Ned", "Nelson", "Nero", "Nico", "Noah", "Norm", "Oakley", "Odie", "Odin", "Oliver",
	"Ollie", "Oreo", "Oscar", "Otis", "Otto", "Ozzy", "Pablo", "Parker", "Peanut", "Pepper",
	"Petey", "Porter", "Prince", "Quincy", "Radar", "Ralph", "Rambo", "Ranger", "Rascal",
	"Rebel", "Reese", "Reggie", "Remy", "Rex", "Ricky", "Rider", "Riley", "Ringo", "Rocco",
	"Rockwell", "Rocky", "Romeo", "Rosco", "Rudy", "Rufus", "Rusty", "Sam", "Sammy", "Samson",
	"Sarge", "Sawyer", "Scooby", "Scooter", "Scout", "Scrappy", "Shadow", "Shamus", "Shiloh",
	"Simba", "Simon", "Smoky", "Snoopy", "Sparky", "Spencer", "Spike", "Spot", "Stanley",
	"Stewie", "Storm", "Taco", "Tank", "Taz", "Teddy", "Tesla", "Theo", "Thor", "Titus", "TJ",
	"Toby", "Trapper", "Tripp", "Tucker", "Tyler", "Tyson", "Vince", "Vinnie", "Wally",
	"Walter", "Watson", "Willy", "Winston", "Woody", "Wrigley", "Wyatt", "Yogi", "Yoshi",
	"Yukon", "Zane", "Zeus", "Ziggy",
}

func chooseDog(names []string, gender string) string {
	name := names[rand.Intn(len(names))]
	dog := Dog{name, gender}

	log.WithFields(log.Fields{
		"name":   dog.Name,
		"gender": dog.Gender,
	}).Info("Generated new dog name")

	res, err := json.Marshal(dog)

	if err != nil {
		fmt.Println(err)
	}

	return string(res)

}

func females(w http.ResponseWriter, r *http.Request) {
	w.Header().Add("content-type", "application/json")

	response := chooseDog(femaleNames, "female")
	fmt.Fprintf(w, string(response))
}

func males(w http.ResponseWriter, r *http.Request) {
	w.Header().Add("content-type", "application/json")

	response := chooseDog(maleNames, "male")
	fmt.Fprintf(w, string(response))
}

func dogs(w http.ResponseWriter, r *http.Request) {
	n := rand.Intn(2)

	if n == 1 {
		males(w, r)
	} else {
		females(w, r)
	}

}

func init() {
	// Log as JSON instead of the default ASCII formatter.
	log.SetFormatter(&log.JSONFormatter{})

	// Output to stdout instead of the default stderr
	// Can be any io.Writer, see below for File example
	log.SetOutput(os.Stdout)

	// Only log the warning severity or above.
	log.SetLevel(log.InfoLevel)
}

func main() {
	rand.Seed(time.Now().Unix())
	http.HandleFunc("/dogs/males", males)
	http.HandleFunc("/dogs/females", females)
	http.HandleFunc("/dogs", dogs)

	err := http.ListenAndServe(Host+":"+Port, nil)
	if err != nil {
		log.Fatal("Error Starting the HTTP Server : ", err)
		return
	}

}
