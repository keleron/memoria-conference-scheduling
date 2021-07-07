#pragma once

#include "vector"

using namespace std;

class Person
{
public:
	int id;
	vector<bool> forbidden;
	Person(int id, int nB);
};

