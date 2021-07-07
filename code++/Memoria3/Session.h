#pragma once

#include "vector"
#include "Article.h"
#include "Person.h"

class Article;

class Session
{
public:
	int id, row, col;
	bool hasBest;
	float cost;
	vector<Article*> articles;
	Person* chair;
	Person* organizer;
	Track* track;
	vector<bool> forbidden;
	Session(int id);
	void computeCost(vector<vector<float>> mat);
	void mixForbidden();
	void updateForbidden();
};

