// Chinese Standard Mahjong sample bot
// random strategy
// modified from http://www.botzone.org/games#Chinese-Standard-Mahjong

#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>

#include "mahjong.h"

using namespace std;

string action(string &requests) {
    istringstream iss(requests);
    vector<string> request, response;
    vector<string> hand;
    
    int turnID;
    string stmp;
    iss >> turnID;
    turnID--;
    getline(iss, stmp);
    for(int i = 0; i < turnID; i++) {
        getline(iss, stmp);
        request.push_back(stmp);
        getline(iss, stmp);
        response.push_back(stmp);
    }
    getline(iss, stmp);
    request.push_back(stmp);

    if(turnID < 2) {
        response.push_back("PASS");
    } else {
        int itmp, myPlayerID, quan;
        ostringstream sout;
        istringstream sin;
        sin.str(request[0]);
        sin >> itmp >> myPlayerID >> quan;
        sin.clear();
        sin.str(request[1]);
        for(int j = 0; j < 5; j++) sin >> itmp;
        for(int j = 0; j < 13; j++) {
            sin >> stmp;
            hand.push_back(stmp);
        }
        for(int i = 2; i < turnID; i++) {
            sin.clear();
            sin.str(request[i]);
            sin >> itmp;
            if(itmp == 2) {
                sin >> stmp;
                hand.push_back(stmp);
                sin.clear();
                sin.str(response[i]);
                sin >> stmp >> stmp;
                hand.erase(find(hand.begin(), hand.end(), stmp));
            }
        }
        sin.clear();
        sin.str(request[turnID]);
        sin >> itmp;
        if(itmp == 2) {
            random_shuffle(hand.begin(), hand.end());
            sout << "PLAY " << *hand.rbegin();
            hand.pop_back();
        } else {
            sout << "PASS";
        }
        response.push_back(sout.str());
    }
    return response[turnID];
}