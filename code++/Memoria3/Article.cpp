#include "Article.h"

Article::Article(int id)
{
	this->id = id;
	this->name = "whocares";
	this->track = nullptr;
	this->author = nullptr;
	this->isBest = false;
}

Article::Article() {
	this->id = 0;
	this->name = "whocares";
	this->track = nullptr;
	this->author = nullptr;
	this->isBest = false;
}

