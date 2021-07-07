#pragma once
#include <vector>
#include "Article.h"
#include "Session.h"
#include "Solver.h"

class Solver;

using namespace std;

class Track
{
public:
	Solver* solver;
	Track(int id, Solver* solver);
	int id, attendance;
	vector<int> waste;
	vector<Person*> chairs, organizers;
	vector<Article*> articles;
	vector<Session*> sessions;
	void fillSessions(int sessionSize);
	void adjustArticlesInSessions();
};

