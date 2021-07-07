#include "Session.h"
#include "Person.h"

Session::Session(int id)
{
	this->id = id;
	this->cost = 0;
	this->hasBest = false;
}

void Session::computeCost(vector<vector<float>> mat)
{
	cost = 0;
	for (size_t i = 0; i < articles.size(); i++)
	{
		int ii = articles[i]->id;
		for (size_t j = 0; j < articles.size(); j++) {
			int jj = articles[j]->id;
			cost += mat[ii][jj];
		}
	}
}

void Session::mixForbidden()
{
	int n = articles[0]->author->forbidden.size();
	forbidden.resize(n, 0);
	for (auto& article : articles) {
		for (size_t i = 0; i < n; i++)
		{
			forbidden[i] = forbidden[i] || article->author->forbidden[i];
		}
	}

}

void Session::updateForbidden()
{
	for (const auto& article : articles) {

	}
}
