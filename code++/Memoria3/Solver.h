#pragma once

#include "Article.h"
#include "vector"
#include "Session.h"
#include "Track.h"
#include "Room.h"
#include "Person.h"
#include <unordered_map>


using namespace std;

class Solver
{
public:
	Solver(unordered_map<string, float> PARAMS);
	int nA, nS, nR, nB, nAS, nT, nP;
	unordered_map<string, float> PARAMS;
	vector<Article*> articles;
	vector<vector<float>> similarity_matrix;
	vector<vector<Session*>> grid;
	vector<Session*> sessions;
	vector<Track*> tracks;
	vector<Room*> rooms;
	vector<Person*> people;
	void read(string filename);
	void reserve();
	void solve();
	vector<Session*> clusterArticles(vector<Article*> articles);
	void buildGrid(vector<Session*> sessions);
	int colCost(int col);
	void writeSolution();

};


