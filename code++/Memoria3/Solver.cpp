#include "Solver.h"

#include <climits>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <algorithm>
#include <random>
#include <stdlib.h> 
#include <unordered_map>

using namespace std;

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
	cout << "INFO: RESERVED SPACE\n";
}

void Solver::solve()
{
	cout << "INFO: INIT CLUSTER SESSIONING\n";
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


	//int step = 0;
	int N = (int)PARAMS["-steps"];
	//Session* sa, * sb;
	float TEMP = PARAMS["-it"];;
	float cooldown = PARAMS["-cr"];
	const float p1 = PARAMS["-p1"], p2 = PARAMS["-p2"], p3 = PARAMS["-p3"], p4 = PARAMS["-p4"];

	for (int i = 0; i < N; i++) {
		float chance = uniform();
		if (chance < p1) {
			int r1 = randint(nR), r2 = randint(nR), c1 = randint(nB), c2 = randint(nB);
			//while (c1 == c2) c2 = randint(nB);
			int delta = -(colCost(c1) + colCost(c2));
			swap(grid[r1][c1], grid[r2][c2]);
			delta += (colCost(c1) + colCost(c2));
			//cout << "swaping " << "(" << r1 << "," << c1 << ")" << "x" << "(" << r2 << "," << c2 << ")\n";
			//cout << "\t" << delta << "\n";
			if (delta <= 0) continue;
			if (exp((float)delta / TEMP) > uniform()) swap(grid[r1][c1], grid[r2][c2]);
		}
		else if (chance < p1 + p2) {
			int r = randint(nR), c = randint(nB);
			while (!grid[r][c]) r = randint(nR), c = randint(nB);
			int delta = -colCost(c);
			Person* oldPerson = grid[r][c]->chair;
			Person* newPerson = grid[r][c]->track->chairs[randint(grid[r][c]->track->chairs.size())];
			grid[r][c]->chair = newPerson;
			delta += colCost(c);
			//cout << "changing chair of " << "(" << r << "," << c << ")\n";
			//cout << "\t" << delta << "\n";
			if (delta <= 0) continue;
			if (exp((float)delta / TEMP) > uniform()) grid[r][c]->chair = oldPerson;
		}
		else if (chance < p1 + p2 + p3) {
			int r = randint(nR), c = randint(nB);
			while (!grid[r][c]) r = randint(nR), c = randint(nB);
			int delta = -colCost(c);
			Person* oldPerson = grid[r][c]->organizer;
			Person* newPerson = grid[r][c]->track->organizers[randint(grid[r][c]->track->organizers.size())];
			grid[r][c]->organizer = newPerson;
			delta += colCost(c);
			//cout << "changing organizer of " << "(" << r << "," << c << ")\n";
			//cout << "\t" << delta << "\n";
			if (delta <= 0) continue;
			if (exp((float)delta / TEMP) > uniform()) grid[r][c]->organizer = oldPerson;
		}
		else if (chance < p1 + p2 + p3 + p4) {
			int t1 = randint(nT);
			while (tracks[t1]->sessions.size() == 1) t1 = randint(nT);
			int s1 = randint(tracks[t1]->sessions.size());
			int s2 = randint(tracks[t1]->sessions.size());
			while (s1 == s2) s2 = randint(tracks[t1]->sessions.size());
			int a1 = randint(nAS), a2 = randint(nAS);
			//while (a1 == a2) a2 = randint(nAS);
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
					if (c1 != -1 && c2 != -1 && r1 != -1 && r2 != -1) goto theEnd;
				}
			}
		theEnd:
			int delta = -(colCost(c1) + colCost(c2));
			swap(grid[r1][c1]->articles[a1], grid[r2][c2]->articles[a2]);
			delta += (colCost(c1) + colCost(c2));
			//int id1 = session1->articles[a1] ? session1->articles[a1]->id : -1;
			//int id2 = session2->articles[a2] ? session2->articles[a2]->id : -1;
			//cout << "swaping articles" << "(" << id1 << "x" << id2 << ") from (a place)\n";
			//cout << "\t" << delta << "\n";
			if (delta <= 0) continue;
			if (exp((float)delta / TEMP) > uniform()) swap(grid[r1][c1]->articles[a1], grid[r2][c2]->articles[a2]);
		}
		TEMP *= cooldown;
	}
	int total_cost = 0;
	for (int i = 0; i < nB; i++)	total_cost += colCost(i);
	std::cout << "INFO: COST AFTER SA " << (int)total_cost << "\n";

	//for (int b = 0; b < nB; b++)
	//{
	//	cout << "INITIAL COL COST " << colCost(b) << "\n";
	//	vector<Session*> column;
	//	for (int r = 0; r < nR; r++) column.push_back(grid[r][b]);
	//	sort(column.begin(), column.end());
	//	vector<Session*> best_order;
	//	int best_cost = INT_MAX;
	//	do {
	//		int local_cost = 0;
	//		for (int r = 0; r < nR; r++)
	//		{
	//			if (!column[r]) continue;
	//			int waste = (column[r]->track->attendance - rooms[r]->capacity);
	//			local_cost += waste > 0 ? waste : 0;
	//		}
	//		if (local_cost < best_cost) {
	//			best_cost = local_cost;
	//			best_order = column;
	//		}
	//	} while (next_permutation(column.begin(), column.end()));
	//	for (int r = 0; r < nR; r++) {
	//		grid[r][b] = best_order[r];
	//	}
	//}
	//total_cost = 0;
	//for (int i = 0; i < nB; i++)	total_cost += colCost(i);
	//std::cout << "INFO: COST AFTER GREEDY POLISH " << (int)total_cost << "\n";
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
	//Session* session;
	unordered_map<int, int> counter;
	for (int i = 0; i < nR; i++)
	{
		if (grid[i][col] == nullptr) { continue; }
		int waste = (grid[i][col]->track->attendance - rooms[i]->capacity);
		cost += waste > 0 ? waste : 0;
		cost += grid[i][col]->chair->forbidden[col] * nAS * COST_AMPLIFIER;
		cost += grid[i][col]->organizer->forbidden[col] * nAS * COST_AMPLIFIER;
		for (const auto& a1 : grid[i][col]->articles)
		{
			if (a1) cost += a1->author->forbidden[col] * nAS * COST_AMPLIFIER;
		}

		for (int j = i + 1; j < nR; j++)
		{
			if (grid[j][col] == nullptr) { continue; }
			cost += (grid[i][col]->chair == grid[j][col]->chair) * nAS * COST_AMPLIFIER;
			cost += (grid[i][col]->organizer == grid[j][col]->organizer) * nAS * COST_AMPLIFIER;
			cost += (grid[i][col]->track == grid[j][col]->track) * nAS * COST_AMPLIFIER;

			for (const auto& a1 : grid[i][col]->articles) {
				if (a1 == nullptr) { continue; }
				cost += (a1->author == grid[j][col]->chair) * nAS * COST_AMPLIFIER;
				cost += (a1->author == grid[j][col]->organizer) * nAS * COST_AMPLIFIER;

				for (const auto& a2 : grid[j][col]->articles) {
					if (a2 == nullptr) { continue; }
					cost += (grid[i][col]->chair == a2->author) * nAS * COST_AMPLIFIER;
					cost += (grid[i][col]->organizer == a2->author) * nAS * COST_AMPLIFIER;
					cost += (a1->author == a2->author ? 1 : 0) * COST_AMPLIFIER;
				}
			}
			/*if (cost > 1000) {
				cout << "cost-inside: " << i << "," << j << "\t" << cost << "\n";
			}*/
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

