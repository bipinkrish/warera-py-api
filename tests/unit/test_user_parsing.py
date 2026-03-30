import json

from warera.models.user import User


def test_user_parsing_from_sample():
    sample_json = """
    {
      "result": {
        "data": {
          "dates": {
            "lastConnectionAt": "2024-01-01T00:00:00.000Z",
            "lastHiresAt": ["2024-01-01T00:00:00.000Z"],
            "lastWorkAt": "2024-01-01T00:00:00.000Z"
          },
          "leveling": {
            "level": 10,
            "totalXp": 1000
          },
          "_id": "mock_user_id",
          "username": "mock_user",
          "country": "mock_country_id",
          "isActive": true,
          "skills": {
            "energy": {
              "level": 1,
              "total": 100
            },
            "attack": {
              "level": 1,
              "total": 100
            }
          },
          "militaryRank": 1,
          "createdAt": "2024-01-01T00:00:00.000Z",
          "stats": {
            "damagesCount": 100
          },
          "rankings": {
            "userDamages": {
              "value": 100,
              "rank": 1,
              "tier": "bronze"
            }
          },
          "avatarUrl": "https://example.com/avatar.jpg",
          "mu": "mock_mu_id"
        }
      }
    }
    """
    data = json.loads(sample_json)["result"]["data"]
    user = User.model_validate(data)
    
    assert user.id == "mock_user_id"
    assert user.username == "mock_user"
    assert user.country == "mock_country_id"
    assert user.is_active is True
    assert user.leveling.level == 10
    assert user.skills.energy.level == 1
    assert user.stats.damages_count == 100
    assert user.rankings.user_damages.tier == "bronze"
    assert user.mu == "mock_mu_id"
    assert user.avatar_url == "https://example.com/avatar.jpg"
    
    # Also ensure UserLite parses correctly and ignores extra fields
    from warera.models.user import UserLite
    user_lite = UserLite.model_validate(data)
    assert user_lite.id == "mock_user_id"
    assert user_lite.leveling.level == 10
    assert user_lite.stats.damages_count == 100
