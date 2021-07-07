#include <list>
#include <iostream>
#include <algorithm>
#include <random>
#include <climits>

#include "Track.h"
#include "Session.h"
#include "Utils.h"
#include "Person.h"


Track::Track(int id, Solver* solver)
{
	this->id = id;
	this->solver = solver;
	this->attendance = 0;
}

void Track::fillSessions(int sessionSize)
{
	int n = (int)ceil((float)articles.size() / (float)sessionSize);
	for (int i = 0; i < n; i++) sessions.push_back(new Session(i));
	for (const auto& session : sessions) {
		session->forbidden.resize(solver->nB, 0);
		session->track = this;
	}
}

void Track::adjustArticlesInSessions()
{
	list<Article*> lst_articles(articles.begin(), articles.end());
	auto it = lst_articles.begin();
	while (it != lst_articles.end()) {
		if ((*it)->isBest) {
			sessions[0]->articles.push_back(*it);
			sessions[0]->forbidden = MixVectors(((*it)->author->forbidden), sessions[0]->forbidden);
			it = lst_articles.erase(it);// erase and go to next
		}
		else { ++it; }
	}

	shuffle(articles.begin(), articles.end(), std::random_device());

	for (const auto& article : lst_articles) {
		Session* best_session = sessions[0];
		int best_session_value = INT_MAX;
		for (const auto& session : sessions) {
			int newCost = newOnesInVector(session->forbidden, article->author->forbidden);
			if (newCost == -1) {
				//std::cout << "IF ARTICLE IS SCHEDULED THERE WILL FILL ALL THE BLOCKS\n";
				continue;
			}
			if (session->articles.size() == solver->nAS) {
				//std::cout << "SESSION REACH MAX ARTICLES\n";
				continue;
			}
			if (session->articles.size() == 0) newCost = 0;

			if (newCost < best_session_value) {
				best_session_value = newCost;
				best_session = session;
			}
		}
		if (best_session_value == INT_MAX) {
			for (const auto& session : sessions) {
				if (session->articles.size() < solver->nAS) {
					best_session = session;
				}
			}
		};
		best_session->articles.push_back(article);
		best_session->forbidden = MixVectors(best_session->forbidden, article->author->forbidden);
	}

	for (auto& session : sessions)
	{
		int random_chair = rand() % chairs.size();
		session->chair = chairs[random_chair];
		int random_org = rand() % organizers.size();
		session->organizer = organizers[random_org];
	}

}
