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

	unordered_map<string, float> PARAMS;
	PARAMS["-cr"] = 0.999;
	PARAMS["-steps"] = 10000000 / 2;
	PARAMS["-mult"] = 1000;
	PARAMS["-seed"] = -1;
	PARAMS["-p1"] = 0.25;
	PARAMS["-p2"] = 0.25;
	PARAMS["-p3"] = 0.25;
	PARAMS["-p4"] = 0.25;
	PARAMS["-weird"] = 0;
	PARAMS["-v"] = 0;
	PARAMS["-stuck"] = 10000;
	PARAMS["-reheat"] = 1000;

	string argument, last = "";


	if (argc < 2) {
		cout << "Not enough parameters, running with --help\n";
		argument = "--help";
	}
	else {
		argument = string(argv[1]);
	}
	if (argument == "--help") {
		cout << "usage: ./executable filename [options]\n";
		cout << "  options:\n";
		cout << "    [-cr]      : Cooling Rate (" << PARAMS["-cr"] << ")\n";
		cout << "    [-steps]   : Steps of Simulated Annealing (" << PARAMS["-steps"] << ")\n";
		cout << "    [-mult]    : Multiplier for hard constraint (" << PARAMS["-mult"] << ")\n";
		cout << "    [-seed]    : Random Seed (" << PARAMS["-seed"] << ")\n";
		cout << "    [-stuck]   : Number of bad solutions to reheat (" << PARAMS["-stuck"] << ")\n";
		cout << "    [-reheat]  : Reheat factor to increase temperature (" << PARAMS["-reheat"] << ")\n";
		cout << "  special ones for each one of the iter of Simulated Annealing:\n";
		cout << "    [-p1]      : Probability of swap two entire sessions (" << PARAMS["-p1"] << ")\n";
		cout << "    [-p2]      : Probability of switch a random chair (" << PARAMS["-p2"] << ")\n";
		cout << "    [-p3]      : Probability of switch a random organizer (" << PARAMS["-p3"] << ")\n";
		cout << "    [-p4]      : Probability of swap two random articles (" << PARAMS["-p4"] << ")\n";
		cout << "-------------------\n";
		cout << "    [-weird]   : <bool> Activate weird SA variant (" << PARAMS["-weird"] << ")\n";
		exit(1);
	}
	for (int i = 2; i < argc; i++)
	{
		argument = string(argv[i]);
		if (argument.find("-") != string::npos) { last = argument; }
		else {
			PARAMS[last] = stof(argument);
			if (PARAMS["-v"] > 1) cout << last << " : " << argument << "\n";
		}
	}
	if (PARAMS["-seed"] != -1) {
		if (PARAMS["-v"] > 1) cout << "-seed : " << (int)PARAMS["-seed"] << "\n";
		srand((int)PARAMS["-seed"]);
	}
	else { srand(time(NULL)); }

	string filename = argv[1];
	cout << filename << ";" << PARAMS["-seed"] << ";";
	string filename_out = filename.substr(0, filename.size() - 3) + ".heu.sol";

	Solver solver(PARAMS);
	solver.read(filename);
	solver.solve();
	solver.writeSolution(filename_out);
}
