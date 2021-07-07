#pragma once

#include <string>
#include <vector>

using namespace std;

class Track;
class Person;

class Article {
public:
	int id;
	string name;
	Track* track;
	Person* author;
	bool isBest;
	Article(int id);
	Article();
};
