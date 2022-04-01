from ...bin.utils import Utils

def check_time_outs(team_side_index, event_id):

    left_team_id, right_team_id, rules_set_id = Utils.api("get",
    model="Event",
    params={"id": event_id},
    fields=["left_team_id", "right_team_id", "rules_set_id"]
    )[0]

    periods_count = Utils.api("get",
    model="Period",
    params={"event_id": event_id},
    fields=["id",]
    )

    latest_period_id = periods_count[-1][0]

    time_outs_per_team_per_period = Utils.api("get",
    model="RulesSet",
    params={"id": rules_set_id},
    fields=["time_outs_per_team_per_period",]
    )[0][0]

    time_outs_count = len(Utils.api("get",
    model="TimeOut",
    params={"event_id": event_id, "period_id": latest_period_id, "team_id": [left_team_id, right_team_id][team_side_index], "is_technical": 0},
    fields=["id",]
    ))

    def check_time_outs_in_period(): # check if any of the teams has a right to a time out in a given period
        return max(eval(time_outs_per_team_per_period)[periods_count - 1]) > 0

    def check_availability(team_side_index): # check if a team has any of the number of time outs available
        return time_outs_count[team_side_index] < eval(time_outs_per_team_per_period)[periods_count - 1][team_side_index]

    return 0 if not (check_time_outs_in_period() and check_availability(team_side_index)) else 1 if check_time_outs_in_period() else 2
