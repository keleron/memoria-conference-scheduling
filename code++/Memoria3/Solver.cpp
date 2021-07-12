#include "Solver.h"

#include <climits>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <algorithm>
#include <random>
#include <unordered_map>
#include <iomanip>
#include <chrono>

using namespace std;
using namespace std::chrono;

int randint(int N = 0) { return rand() % N; }
float uniform() { return (float)rand() / (RAND_MAX); };

Solver::Solver(unordered_map<string, float> PARAMS)
{
	this->PARAMS = PARAMS;
}

void Solver::read(string filename)
{
	int dummy;
	string line;
	ifstream file(filename);
	getline(file, line);
	file >> nA >> nP >> nB >> nR >> nT >> nAS >> dummy;
	grid = vector<vector<Session*>>(nR, vector<Session*>(nB, nullptr));

	getline(file, line);
	getline(file, line);
	reserve();

	for (int i = 0; i < nA; i++)
	{
		int id, track, author;
		bool isBest;
		file >> id >> track >> author >> isBest;
		articles[id]->id;
		articles[id]->track = tracks[track];
		articles[id]->author = people[author];
		articles[id]->isBest = isBest;
		tracks[track]->articles.push_back(articles[id]);
	}

	getline(file, line);
	getline(file, line);

	//THIS IS FOR PERSON
	for (int i = 0; i < nP; i++)
	{
		int _id, n;
		getline(file, line);
		istringstream is(line);
		is >> _id;
		while (is >> n) people[_id]->forbidden[n] = true;
	}
	getline(file, line);

	//TRACK HISTORIC ATTENDANCE 
	for (int i = 0; i < nT; i++)	file >> dummy >> tracks[i]->attendance;

	getline(file, line);
	getline(file, line);

	//ROOM CAPACITY
	for (int i = 0; i < nR; i++) file >> dummy >> rooms[i]->capacity;

	//TRACK	CHAIRS
	getline(file, line);
	getline(file, line);
	for (int i = 0; i < nT; i++)
	{
		int _id, n;
		getline(file, line);
		istringstream is(line);
		is >> _id;
		while (is >> n) tracks[_id]->chairs.push_back(people[n]);
	}
	getline(file, line);

	// TRACK	ORGANIZADORES
	for (int i = 0; i < nT; i++)
	{
		int _id, n;
		getline(file, line);
		istringstream is(line);
		is >> _id;
		while (is >> n) tracks[_id]->organizers.push_back(people[n]);
	}
	for (int t = 0; t < nT; t++)
	{
		for (int r = 0; r < nR; r++) {
			int waste = abs(tracks[t]->attendance - rooms[r]->capacity);
			tracks[t]->waste.push_back(waste);
		}
	}
}

void Solver::reserve()
{
	for (int i = 0; i < nA; i++) articles.push_back(new Article(i));
	for (int i = 0; i < nT; i++) tracks.push_back(new Track(i, this));
	for (int i = 0; i < nR; i++) rooms.push_back(new Room(i));
	for (int i = 0; i < nP; i++) people.push_back(new Person(i, nB));
}

void Solver::solve()
{

	if (PARAMS["-v"] > 0) cout << "INFO: RUNNING CREATION OF SESSIONS\n";
	high_resolution_clock::time_point t1 = high_resolution_clock::now();
	for (const auto& track : tracks) {
		track->fillSessions(nAS);
		track->adjustArticlesInSessions();
	}
	int i = 0;
	for (const auto& track : tracks)
	{
		for (auto& session : track->sessions) {
			session->id = i;
			while (session->articles.size() < (size_t)nAS) session->articles.push_back(nullptr);
			sessions.push_back(session);
			i++;
		}
	}
	if (sessions.size() > grid.size() * grid[0].size()) {
		cout << "INFEASIBLE\n";
		exit(1);
	};
	for (size_t i = 0; i < sessions.size(); i++) grid[i / nB][i % nB] = sessions[i];

	int total_cost = 0;
	for (int i = 0; i < nB; i++) total_cost += colCost(i);
	if (PARAMS["-v"] > 0) cout << "\nINFO: INITIAL COST " << total_cost << "\n";

	int N = (int)PARAMS["-steps"];

	float TEMP = total_cost * 2;
	float cooldown = PARAMS["-cr"];
	float p1 = PARAMS["-p1"], p2 = PARAMS["-p2"], p3 = PARAMS["-p3"], p4 = PARAMS["-p4"];
	bool weird_mode = (bool)PARAMS["-weird"];
	int bad_sol_counter = 0;
	int global_best = INT_MAX;

	for (int i = 0; i < N; i++) {

		if (bad_sol_counter > PARAMS["-stuck"]) {
			int local_full_cost = 0;
			for (int i = 0; i < nB; i++) local_full_cost += colCost(i);
			if (local_full_cost < global_best) global_best = local_full_cost;
			float new_temp = TEMP + (PARAMS["-reheat"] - (PARAMS["-reheat"] - 1) * (float)i / (float)N);
			if (PARAMS["-v"] > 0) cout << i << " LOCAL OPTIMA IN " << local_full_cost << " NEED RE HEAT " << TEMP << "->" << new_temp << "\n";
			TEMP = new_temp;
			bad_sol_counter = 0;
		}
		float chance = uniform();
		if (chance < p1) {
			int r1 = randint(nR), r2 = randint(nR), c1 = randint(nB), c2 = randint(nB);
			int delta = -(colCost(c1) + colCost(c2));
			swap(grid[r1][c1], grid[r2][c2]);
			delta += (colCost(c1) + colCost(c2));
			if (delta >= 0) {
				if (weird_mode) {
					if (exp((float)delta / TEMP) > uniform()) swap(grid[r1][c1], grid[r2][c2]);
				}
				else {
					if (exp(-(float)delta / TEMP) <= uniform()) swap(grid[r1][c1], grid[r2][c2]);
				}
				bad_sol_counter++;
			}
			else {
				bad_sol_counter = 0;
			}
		}
		else if (chance < p1 + p2) {
			int r = randint(nR), c = randint(nB);
			while (!grid[r][c]) r = randint(nR), c = randint(nB);
			int delta = -colCost(c);
			Person* oldPerson = grid[r][c]->chair;
			Person* newPerson = grid[r][c]->track->chairs[randint(grid[r][c]->track->chairs.size())];
			grid[r][c]->chair = newPerson;
			delta += colCost(c);
			if (delta >= 0) {
				if (weird_mode) {
					if (exp((float)delta / TEMP) > uniform()) grid[r][c]->chair = oldPerson;
				}
				else {
					if (exp(-(float)delta / TEMP) <= uniform()) grid[r][c]->chair = oldPerson;
				}
				bad_sol_counter++;
			}
			else {
				bad_sol_counter = 0;
			}
		}
		else if (chance < p1 + p2 + p3) {
			int r = randint(nR), c = randint(nB);
			while (!grid[r][c]) r = randint(nR), c = randint(nB);
			int delta = -colCost(c);
			Person* oldPerson = grid[r][c]->organizer;
			Person* newPerson = grid[r][c]->track->organizers[randint(grid[r][c]->track->organizers.size())];
			grid[r][c]->organizer = newPerson;
			delta += colCost(c);
			if (delta >= 0) {
				if (weird_mode) {
					if (exp((float)delta / TEMP) > uniform()) grid[r][c]->organizer = oldPerson;
				}
				else {
					if (exp(-(float)delta / TEMP) <= uniform()) grid[r][c]->organizer = oldPerson;
				}
				bad_sol_counter++;
			}
			else {
				bad_sol_counter = 0;
			}
		}
		else if (chance <= p1 + p2 + p3 + p4) {
			int t1 = randint(nT);
			while (tracks[t1]->sessions.size() == 1) t1 = randint(nT);
			int s1 = randint(tracks[t1]->sessions.size());
			int s2 = randint(tracks[t1]->sessions.size());
			while (s1 == s2) s2 = randint(tracks[t1]->sessions.size());
			int a1 = randint(nAS), a2 = randint(nAS);
			Track* track = tracks[t1];
			Session* session1 = track->sessions[s1];
			Session* session2 = track->sessions[s2];
			bool isbest1 = session1->articles[a1] ? session1->articles[a1]->isBest : false;
			bool isbest2 = session2->articles[a2] ? session2->articles[a2]->isBest : false;
			if (isbest1 || isbest2) continue;

			int c1 = -1, r1 = -1, c2 = -1, r2 = -2;
			for (int r = 0; r < nR; r++)
			{
				for (int b = 0; b < nB; b++)
				{
					if (grid[r][b] == session1) {
						r1 = r;
						c1 = b;
					}
					if (grid[r][b] == session2) {
						c2 = b;
						r2 = r;
					}
					if (c1 != -1 && c2 != -1) goto theEnd;
				}
			}
		theEnd:
			int delta = -(colCost(c1) + colCost(c2));
			swap(grid[r1][c1]->articles[a1], grid[r2][c2]->articles[a2]);
			delta += (colCost(c1) + colCost(c2));
			if (delta >= 0) {
				if (weird_mode) {
					if (exp((float)delta / (float)TEMP) > uniform()) swap(grid[r1][c1]->articles[a1], grid[r2][c2]->articles[a2]);
				}
				else {
					if (exp(-(float)delta / (float)TEMP) <= uniform()) swap(grid[r1][c1]->articles[a1], grid[r2][c2]->articles[a2]);
				}
				bad_sol_counter++;
			}
			else {
				bad_sol_counter = 0;
			}

		}
		TEMP *= cooldown;
	}
	high_resolution_clock::time_point t2 = high_resolution_clock::now();
	auto duration = duration_cast<seconds>(t2 - t1).count();
	cout << "INFO: BEST COST FOUND " << global_best << "\n";
	cout << "INFO: TIME ELAPSED " << duration << "[s]\n";
}

vector<Session*> Solver::clusterArticles(vector<Article*> articles)
{
	vector<Article*> shuffled;
	sample(articles.begin(), articles.end(), std::back_inserter(shuffled), articles.size(),
		std::mt19937{ std::random_device{}() }
	);
	int nS = (int)ceil((float)articles.size() / (float)nAS);
	vector<Session*> sessions;
	for (int i = 0; i < nS; i++) sessions.push_back(new Session(i));
	for (size_t i = 0; i < articles.size(); i++)
	{
		sessions[i / nAS]->articles.push_back(articles[i]);
		if (articles[i]->isBest) sessions[i / nAS]->hasBest = true;
	}
	return sessions;
}

void Solver::buildGrid(vector<Session*> sessions)
{
	int i = 0;
	for (auto& session : sessions) {
		grid[i / nR][i % nB] = session;
		i++;
	}

}

int Solver::colCost(int col)
{
	int cost = 0;
	int COST_AMPLIFIER = (int)PARAMS["-mult"];
	unordered_map<int, int> counter;
	int nASCOST = nAS * COST_AMPLIFIER;
	for (int i = 0; i < nR; i++)
	{
		if (grid[i][col] == nullptr) { continue; }
		int waste = (grid[i][col]->track->attendance - rooms[i]->capacity);
		cost += waste > 0 ? waste : 0;
		cost += grid[i][col]->chair->forbidden[col] * nASCOST;
		cost += grid[i][col]->organizer->forbidden[col] * nASCOST;
		for (const auto& a1 : grid[i][col]->articles)
		{
			if (a1) cost += a1->author->forbidden[col] * nASCOST;
		}
		for (int j = i + 1; j < nR; j++)
		{
			if (grid[j][col] == nullptr) { continue; }
			cost += (grid[i][col]->chair == grid[j][col]->chair) * nASCOST;
			cost += (grid[i][col]->organizer == grid[j][col]->organizer) * nASCOST;
			cost += (grid[i][col]->track == grid[j][col]->track) * nASCOST;
			for (size_t a1 = 0; a1 < nAS; a1++)
			{
				Article* aa1 = grid[i][col]->articles[a1];
				Article* aa2 = grid[j][col]->articles[a1];
				if (aa1 == nullptr || aa2 == nullptr) { continue; }
				cost += (aa1->author == grid[j][col]->chair) * nASCOST;
				cost += (aa1->author == grid[j][col]->organizer) * nASCOST;
				cost += (grid[i][col]->chair == aa2->author) * nASCOST;
				cost += (grid[i][col]->organizer == aa2->author) * nASCOST
					;
				cost += (aa1->author == aa2->author ? 1 : 0) * COST_AMPLIFIER;
			}
		}
	}
	return cost;
}

void Solver::writeSolution(string filename)
{
	ofstream myfile;
	myfile.open(filename);
	myfile << filename << "\n";
	//ARTICULO # AUTOR
	for (const auto& row : grid)
	{
		for (const auto& session : row) {
			if (!session) {
				for (int i = 0; i < nAS; i++) myfile << "-1;";
				myfile << ";";
				continue;
			}
			for (const auto& article : session->articles) {
				if (!article) {
					myfile << -1 << ";";
					continue;
				}
				myfile << article->id << (article->isBest ? "*" : "") << ";";
			}
			myfile << ";";
		}
		myfile << "\n";
	}
	myfile << "\n";
	//SOLO AUTORES
	for (const auto& row : grid)
	{
		for (const auto& session : row) {
			if (!session) {
				for (int i = 0; i < nAS; i++) myfile << "-1;";
				myfile << ";";
				continue;
			}
			for (const auto& article : session->articles) {
				if (!article) {
					myfile << -1 << ";";
					continue;
				}
				myfile << article->author->id << ";";
			}
			myfile << ";";
		}
		myfile << "\n";
	}
	myfile << "\n";

	//SOLO CHAIRS
	for (const auto& row : grid) {
		for (const auto& session : row) {
			if (!session) {
				for (int i = 0; i < nAS; i++) myfile << "-1;";
				myfile << ";";
				continue;
			}
			myfile << session->chair->id << ";";
			for (int i = 1; i < nAS; i++) myfile << ";";
			myfile << ";";
		}
		myfile << "\n";
	}
	myfile << "\n";
	//SOLO ORGANIZADORES
	for (const auto& row : grid) {
		for (const auto& session : row) {
			if (!session) {
				for (int i = 0; i < nAS; i++) myfile << "-1;";
				myfile << ";";
				continue;
			}
			myfile << session->organizer->id << ";";
			for (int i = 1; i < nAS; i++) myfile << ";";
			myfile << ";";
		}
		myfile << "\n";
	}
	myfile << "\n";
	for (const auto& row : grid) {
		for (const auto& session : row) {
			if (!session) { myfile << "-1;"; }
			else { myfile << session->track->id << ";"; }
		}
		myfile << "\n";
	}
	myfile.close();
}

