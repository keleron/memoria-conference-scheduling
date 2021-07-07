#include "Utils.h"

vector<bool> MixVectors(vector<bool> a, vector<bool> b)
{
	vector<bool> out(a.size(), false);
	for (size_t i = 0; i < a.size(); i++) out[i] = a[i] || b[i];
	return out;
}

int newOnesInVector(vector<bool> a, vector<bool> b)
{
	int sum = 0;
	bool invalid = true;
	for (size_t i = 0; i < a.size(); i++) sum += !a[i] && b[i] ? 1 : 0;
	for (size_t i = 0; i < a.size(); i++) invalid *= a[i] || b[i] ? 1 : 0;
	return invalid ? -1 : sum;
}
