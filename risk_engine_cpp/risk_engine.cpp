#include "risk_engine.h"

double calculate_risk(double speed, double obstacle_distance) {
    return speed / (obstacle_distance + 1.0);
}
