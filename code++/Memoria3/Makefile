output: main.o Article.o Person.o Room.o Session.o Solver.o Track.o Utils.o
	g++ -Wall main.o Article.o Person.o Room.o Session.o Solver.o Track.o Utils.o -o output

main.o: main.cpp
	g++ -Wall -std=c++17 -c main.cpp

Article.o: Article.cpp Article.h
	g++ -Wall -std=c++17 -c Article.cpp

Person.o: Person.cpp Person.h
	g++ -Wall -std=c++17 -c Person.cpp

Room.o: Room.cpp Room.h
	g++ -Wall -std=c++17 -c Room.cpp

Session.o: Session.cpp Session.h
	g++ -Wall -std=c++17 -c Session.cpp

Solver.o: Solver.cpp Solver.h
	g++ -Wall -std=c++17 -c Solver.cpp

Track.o: Track.cpp Track.h
	g++ -Wall -std=c++17 -c Track.cpp

Utils.o: Utils.cpp Utils.h
	g++ -Wall -std=c++17 -c Utils.cpp

clean:
	rm *.o output
