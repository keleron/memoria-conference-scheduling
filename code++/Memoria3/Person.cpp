#include "Person.h"

Person::Person(int id, int nB)
{
	this->id = id;
	this->forbidden.resize(nB, 0);
}
