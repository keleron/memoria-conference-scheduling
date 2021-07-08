// Memoria3.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <string>
#include <unordered_map>
#include "Solver.h"
#include <ctime>

using namespace std;

int main(int argc, char* argv[])
{
	if (argc < 2) {
		cout << "Not enough parameters, run with --help\n";
		exit(0);
	}

	unordered_map<string, float> PARAMS;
	PARAMS["-cr"] = 0.99;
	PARAMS["-steps"] = 10000;
	PARAMS["-it"] = 100;
	PARAMS["-mult"] = 1000;
	PARAMS["-seed"] = -1;
	PARAMS["-p1"] = 0.25;
	PARAMS["-p2"] = 0.25;
	PARAMS["-p3"] = 0.25;
	PARAMS["-p4"] = 0.25;
	string argument, last = "";


	argument = string(argv[1]);
	if (argument == "--help") {
		cout << "usage: ./executable filename [options]\n";
		cout << "  options:\n";
		cout << "    [-cr]      : Cooling Rate (" << PARAMS["-cr"] << ")\n";
		cout << "    [-steps]   : Steps of Simulated Annealing (" << PARAMS["-steps"] << ")\n";
		cout << "    [-it]      : Initial Temperature (" << PARAMS["-it"] << ")\n";
		cout << "    [-mult]    : Multiplier for hard constraint (" << PARAMS["-mult"] << ")\n";
		cout << "    [-seed]    : Random Seed (" << PARAMS["-seed"] << ")\n";
		cout << "  special ones for each one of the iter of Simulated Annealing:\n";
		cout << "    [-p1]      : Probability of swap two entire sessions (" << PARAMS["-p1"] << ")\n";
		cout << "    [-p2]      : Probability of switch a random chair (" << PARAMS["-p2"] << ")\n";
		cout << "    [-p3]      : Probability of switch a random organizer (" << PARAMS["-p3"] << ")\n";
		cout << "    [-p4]      : Probability of swap two random articles (" << PARAMS["-p4"] << ")\n";
		exit(1);
	}
	for (int i = 2; i < argc; i++)
	{
		argument = string(argv[i]);
		if (argument.find("-") != string::npos) { last = argument; }
		else { PARAMS[last] = stof(argument); }
	}
	if (PARAMS["-seed"] != -1) {
		cout << "SETTING CUSTOM SEED TO " << (int)PARAMS["-seed"] << "\n";
		srand((int)PARAMS["-seed"]);
	}
	else { srand(time(NULL)); }

	string filename = argv[1];
	string filename_out = filename.substr(0, filename.size() - 3) + ".heu.sol";

	Solver solver(PARAMS);
	solver.read(filename);
	solver.solve();
	solver.writeSolution(filename_out);
}
