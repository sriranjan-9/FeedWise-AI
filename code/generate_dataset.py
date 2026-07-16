"""
FeedWise Prototype - Synthetic Dataset Generator
--------------------------------------------------
Generates a fake "social media" dataset of posts with deliberately
skewed category distribution, so a simple engagement-optimized
recommender can plausibly get "stuck" recommending one category
repeatedly (needed to demonstrate FeedWise's repetition detection).
"""

import json
import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible dataset

CATEGORIES = {
    # category: (weight, list of creator name pools)
    "Comedy":    {"weight": 16, "creators": ["LaughTrack", "JokesterJay", "PunPatrol", "GiggleGuru"]},
    "Gaming":    {"weight": 13, "creators": ["PixelPete", "RespawnRhea", "GG_Nova", "QuestQueen"]},
    "News":      {"weight": 5,  "creators": ["DailyDesk", "FactFinder", "TheWireUp"]},
    "Sports":    {"weight": 7,  "creators": ["CourtSideCarl", "GoalGetterG", "TrackStarTia"]},
    "Cooking":   {"weight": 4,  "creators": ["ChefBySide", "SimmerSim", "KitchenKay"]},
    "Fitness":   {"weight": 3,  "creators": ["FlexFinn", "CardioCara", "LiftLogan"]},
    "Music":     {"weight": 4,  "creators": ["BeatBrie", "TheMixMaster", "LyricLane"]},
    "Fashion":   {"weight": 3,  "creators": ["StyleSage", "ThreadThea"]},
    "Tech":      {"weight": 3,  "creators": ["ByteBianca", "CircuitCole"]},
    "Travel":    {"weight": 2,  "creators": ["WanderWes", "RoamRia"]},
    "Academics": {"weight": 11, "creators": ["PhysicsPhoebe", "ChemCarter", "MathMotive", "BioBrooke", "AlgoAdrian", "CompSciCasey", "LawrenceLegal", "SocialSage"]},
    "Arts":      {"weight": 4,  "creators": ["PaintPia", "SketchSam", "ArtsyAva", "ClaySage"]},
    "Edits":     {"weight": 6,  "creators": ["EditsByEzra", "MontageMax", "SceneSlicer", "AestheticAri"]},
    "Cars":      {"weight": 3,  "creators": ["RevRico", "DriftDante", "GarageGwen", "TorqueTia"]},
    "Anime":     {"weight": 5,  "creators": ["ArcAnaya", "ShonenSam", "MangaMira", "OtakuOwen"]},
    "Pets":      {"weight": 4,  "creators": ["PawsomePaige", "WhiskerWes", "BarkleyBea", "FluffFinn"]},
    "Finance":   {"weight": 4,  "creators": ["StackSage", "MarketMara", "BudgetBo", "YieldYara"]},
    "DIY":       {"weight": 3,  "creators": ["HackHarlow", "FixItFiona", "GlueGunGus", "ScrapSol"]},
    "Trending":  {"weight": 3,  "creators": ["ViralVee", "TrendTana", "ForYouFae", "ClipClout"]},
    "Science":   {"weight": 5,  "creators": ["CosmoCleo", "LabLeo", "NeuroNina", "QuarkQuinn"]},
    "History":   {"weight": 4,  "creators": ["PastPercy", "ChronoChloe", "RelicRhea", "EpochEli"]},
    "BookTok":   {"weight": 3,  "creators": ["PageParker", "NovelNoor", "ChapterCho", "InkIvy"]},
    "Motivation":{"weight": 3,  "creators": ["DriveDeng", "GritGabe", "RiseRoya", "FocusFern"]},
    "Photography":{"weight": 3, "creators": ["LensLuca", "ShutterShay", "FrameFinn", "ApertureAmi"]},
    "FoodReviews":{"weight": 4, "creators": ["BiteBlake", "TastyTom", "SnackSasha", "CraveCleo"]},
}

TITLE_TEMPLATES = {
    "Comedy":  ["You won't believe what happened at {place}", "Try not to laugh challenge #{n}",
                "My {relative} did THIS and I'm crying", "POV: when {situation}"],
    "Gaming":  ["Insane clutch in {game} ranked", "New {game} update breakdown", "Speedrunning {game} world record attempt",
                "Reacting to {game} lore theories", "{game} boss fight but I'm not allowed to take damage"],
    "News":    ["Breaking: updates on {topic}", "What you need to know about {topic}", "Explainer: {topic} in 60 seconds"],
    "Sports":  ["Top 10 plays from {event}", "{event} highlights you missed", "Reaction to last night's {event}",
                "Football skills that broke the internet", "Match analysis: how that goal actually happened"],
    "Cooking": ["5-minute {dish} recipe", "How to make {dish} like a pro", "{dish} but make it healthy"],
    "Fitness": ["30-day {goal} challenge day #{n}", "Beginner {goal} routine", "Why your {goal} plan isn't working"],
    "Music":   ["New single drop: {song}", "Behind the scenes of {song}", "Reacting to {song} for the first time"],
    "Fashion": ["Outfit ideas for {season}", "Thrift flip transformation #{n}", "{season} capsule wardrobe"],
    "Tech":    ["Is the new {gadget} worth it?", "{gadget} unboxing and first impressions", "5 hidden features of {gadget}"],
    "Travel":  ["Hidden gems in {place}", "48 hours in {place}", "Budget travel guide to {place}"],
    "Academics": ["Why {topic2} actually makes sense once you see this", "The {topic2} concept that breaks everyone's brain",
                  "Explaining {topic2} in under a minute", "The experiment that proves {topic2}",
                  "{topic2} explained with zero jargon", "How I finally understood {topic2}"],
    "Arts":    ["Painting a {artsubject} in one sitting", "Sketching {artsubject} from scratch", "Watch this {artsubject} come to life",
                "The technique every {artsubject} artist should know"],
    "Edits":   ["{character} edit that lives in my head rent free", "{character} edit // {song}",
                "why is this {character} edit so clean", "{character} but every cut is on beat",
                "the {character} edit that broke edit-tok"],
    "Cars":    ["{car} pull that will wake the neighborhood", "POV: {car} launch control",
                "{car} vs {car2} — who wins?", "rating {car} exhaust notes", "{car} build update: episode #{n}"],
    "Anime":   ["This {anime} fight scene still isn't topped", "Ranking every {anime} opening",
                "The {anime} arc that changed everything", "POV: you just finished {anime}",
                "Underrated {anime} moments nobody talks about"],
    "Pets":    ["My {pet} reacts to {situation2}", "My {pet} does the funniest thing every morning",
                "Rating my {pet}'s reaction to {situation2}", "Day in the life of my {pet}",
                "My {pet} vs cucumber — the sequel"],
    "Finance": ["How I saved {money} in 3 months", "The {finance_topic} nobody explains properly",
                "Why your {finance_topic} advice is wrong", "I tried the {finance_topic} trend for 30 days",
                "{finance_topic} explained like you're 12"],
    "DIY":     ["Fixing {broken_thing} for under {money}", "{duration}-minute {broken_thing} hack that actually works",
                "Turning a {broken_thing} into something useful", "DIY {broken_thing} fix nobody tells you about"],
    "Trending": ["everyone's doing the {trend_name} challenge and I had to try it", "the {trend_name} sound that's taking over right now",
                 "explaining {trend_name} for people who don't get it", "{trend_name} but make it chaotic",
                 "why is {trend_name} everywhere right now"],
    "Science": ["What actually happens inside {sci_thing}", "The truth about {sci_thing} they didn't teach you",
                "{sci_thing} explained in 60 seconds", "Why {sci_thing} is way weirder than you think",
                "The science of {sci_thing}, simplified"],
    "History": ["The story of {hist_thing} nobody tells you", "What really happened during {hist_thing}",
                "{hist_thing} in under a minute", "The wildest facts about {hist_thing}",
                "How {hist_thing} changed everything"],
    "BookTok": ["The book that wrecked me: {book_vibe}", "if you liked {book_vibe}, read this next",
                "POV: you just finished a {book_vibe} book", "rating {book_vibe} books I read this month",
                "this {book_vibe} plot twist broke me"],
    "Motivation": ["The {mot_topic} habit that changed my life", "Why discipline beats motivation every time",
                   "Do this every morning for better {mot_topic}", "The {mot_topic} mindset shift nobody talks about",
                   "5 minutes on {mot_topic} that actually helps"],
    "Photography": ["How I shot this {photo_subject} photo", "{photo_subject} photography tips for beginners",
                    "The settings behind this {photo_subject} shot", "editing a {photo_subject} photo start to finish",
                    "why {photo_subject} photography is harder than it looks"],
    "FoodReviews": ["Trying the viral {food_item} everyone's talking about", "Rating {food_item} from 1 to 10",
                    "Is the {food_item} hype actually real?", "I tried {food_item} so you don't have to",
                    "the {food_item} that lived up to the hype"],
}

FILL = {
    "place": ["Tokyo", "the mall", "school", "a wedding", "Paris", "the airport", "Bali"],
    "relative": ["little brother", "grandma", "cousin", "dog", "roommate"],
    "situation": ["the WiFi goes down", "finals week hits", "you oversleep", "the group project falls apart"],
    "game": ["Valorant", "Minecraft", "Fortnite", "Elden Ring", "League of Legends", "Baldur's Gate 3", "Hollow Knight"],
    "topic": ["the election", "climate policy", "the tech industry", "the economy"],
    "event": ["the finals", "the derby", "the championship", "the playoffs"],
    "dish": ["ramen", "pasta", "tacos", "pancakes", "curry"],
    "goal": ["strength", "cardio", "flexibility", "mobility"],
    "song": ["Neon Skies", "Paper Hearts", "Midnight Drive", "Fading Static"],
    "season": ["summer", "fall", "winter", "spring"],
    "gadget": ["phone", "earbuds", "smartwatch", "laptop"],
    "topic2": ["projectile motion", "electron orbitals", "chemical equilibrium", "Newton's third law",
               "acid-base reactions", "wave interference", "thermodynamics", "molecular bonding",
               "Big-O notation", "recursion", "binary search trees", "quantum superposition",
               "how neural networks actually learn", "why hash maps are O(1)", "special relativity",
               "redox reactions", "catalysts", "the periodic table's hidden logic",
               "mathematical induction", "the meaning of a limit", "matrix determinants",
               "probability paradoxes", "imaginary numbers", "differential calculus",
               "the Fibonacci sequence in nature", "prime number mysteries",
               "contract formation", "burden of proof", "landmark court cases",
               "how laws actually get made", "legal precedent", "constitutional rights",
               "what due process actually means", "how the jury system works",
               "why empires collapse", "propaganda techniques", "supply and demand",
               "conformity psychology", "how elections actually work", "GDP's biggest blind spot",
               "why groupthink happens", "the sociology of social media itself"],
    "artsubject": ["portrait", "landscape", "still life", "abstract piece", "charcoal sketch", "ceramic bowl"],
    "character": ["Dexter", "Homelander", "Levi Ackerman", "John Wick", "Arthur Morgan", "Geralt", "Killmonger"],
    "car": ["the R34 GT-R", "an RX-7", "a Supra", "a Civic Type R", "an M3", "a 911 GT3", "an Evo IX"],
    "car2": ["a Mustang GT", "an STI", "an AMG", "a Huracan", "a Type R"],
    "anime": ["Jujutsu Kaisen", "Attack on Titan", "Demon Slayer", "One Piece", "Frieren", "Chainsaw Man"],
    "pet": ["cat", "golden retriever", "parrot", "hamster", "corgi", "bearded dragon"],
    "situation2": ["a vacuum cleaner", "fireworks outside", "its own reflection", "a cucumber", "the doorbell", "a new sibling"],
    "money": ["$500", "$1,200", "$3,000", "$800"],
    "finance_topic": ["credit score", "index fund", "budgeting method", "side hustle", "emergency fund", "compound interest"],
    "broken_thing": ["headphones", "squeaky door", "phone case", "wobbly chair", "charging cable", "shoe sole"],
    "trend_name": ["silent walking", "mob wife aesthetic", "de-influencing", "75 hard", "romanticizing your commute"],
    "duration": ["5", "10", "3", "15", "7"],
    "sci_thing": ["a black hole", "your immune system", "lightning", "the deep ocean", "DNA", "the human brain", "a supernova"],
    "hist_thing": ["the Roman Empire", "the space race", "ancient Egypt", "the printing press", "the Silk Road", "the Cold War"],
    "book_vibe": ["dark academia", "enemies-to-lovers", "cozy fantasy", "sci-fi thriller", "slow-burn romance", "dystopian"],
    "mot_topic": ["focus", "discipline", "confidence", "consistency", "productivity", "your morning routine"],
    "photo_subject": ["street", "portrait", "landscape", "night sky", "macro", "golden hour"],
    "food_item": ["ramen spot", "street taco", "viral pasta", "hole-in-the-wall burger", "matcha place", "dumpling stall"],
}

# Which fill-key drives the subtopic for each category, plus how raw fill
# values map to clean subtopic labels shown in the goal picker.
SUBTOPIC_CONFIG = {
    "Academics": {
        "fill_key": "topic2",
        "map": {
            "projectile motion": "Physics", "Newton's third law": "Physics",
            "wave interference": "Physics", "thermodynamics": "Physics",
            "special relativity": "Physics", "quantum superposition": "Physics",
            "electron orbitals": "Chemistry", "chemical equilibrium": "Chemistry",
            "acid-base reactions": "Chemistry", "molecular bonding": "Chemistry",
            "redox reactions": "Chemistry", "catalysts": "Chemistry", "the periodic table's hidden logic": "Chemistry",
            "Big-O notation": "Computer Science", "recursion": "Computer Science",
            "binary search trees": "Computer Science", "why hash maps are O(1)": "Computer Science",
            "how neural networks actually learn": "Computer Science",
            "mathematical induction": "Math", "the meaning of a limit": "Math",
            "matrix determinants": "Math", "probability paradoxes": "Math", "imaginary numbers": "Math",
            "differential calculus": "Math", "the Fibonacci sequence in nature": "Math", "prime number mysteries": "Math",
            "contract formation": "Law", "burden of proof": "Law",
            "landmark court cases": "Law", "how laws actually get made": "Law",
            "legal precedent": "Law", "constitutional rights": "Law",
            "what due process actually means": "Law", "how the jury system works": "Law",
            "why empires collapse": "Social Science", "propaganda techniques": "Social Science",
            "supply and demand": "Social Science", "conformity psychology": "Social Science",
            "how elections actually work": "Social Science", "GDP's biggest blind spot": "Social Science",
            "why groupthink happens": "Social Science", "the sociology of social media itself": "Social Science",
        },
    },
    "Gaming": {
        "fill_key": "game",
        "map": {
            "Valorant": "FPS / Shooters", "Fortnite": "FPS / Shooters",
            "Minecraft": "Sandbox / Building",
            "Elden Ring": "RPG / Souls-likes", "Baldur's Gate 3": "RPG / Souls-likes",
            "League of Legends": "MOBA / Strategy",
            "Hollow Knight": "Indie / Metroidvania",
            "chess": "Physical / Tabletop", "a ping pong rally": "Physical / Tabletop",
            "board game night": "Physical / Tabletop", "a rock climbing route": "Physical / Tabletop",
        },
    },
    "Anime": {
        "fill_key": "anime",
        "map": {
            "Jujutsu Kaisen": "Shonen / Action", "Demon Slayer": "Shonen / Action",
            "One Piece": "Shonen / Action", "Chainsaw Man": "Shonen / Action",
            "Attack on Titan": "Dark / Seinen",
            "Frieren": "Fantasy / Adventure",
        },
    },
    "Science": {
        "fill_key": "sci_thing",
        "map": {
            "a black hole": "Space & Astro", "a supernova": "Space & Astro",
            "your immune system": "Biology & Body", "DNA": "Biology & Body",
            "the human brain": "Biology & Body",
            "lightning": "Earth & Physics", "the deep ocean": "Earth & Physics",
        },
    },
}


PHYSICAL_GAMES = ["chess", "a ping pong rally", "board game night", "a rock climbing route"]
PHYSICAL_GAME_TEMPLATES = [
    "why {game} is secretly one of the hardest games out there",
    "{game} but everyone's actually trying to win",
    "the strategy behind {game} nobody talks about",
    "POV: {game} gets way more competitive than expected",
]
PHYSICAL_GAME_PROBABILITY = 0.18  # how often a Gaming post is physical/tabletop instead of video game


def make_title(category, n):
    # Gaming gets a special branch: decide physical-vs-video-game FIRST, then
    # pick a matching template, so the two never get mismatched (e.g. "chess
    # boss fight" from a video-game template accidentally applied to chess).
    if category == "Gaming" and random.random() < PHYSICAL_GAME_PROBABILITY:
        game_value = random.choice(PHYSICAL_GAMES)
        template = random.choice(PHYSICAL_GAME_TEMPLATES)
        title = template.format(game=game_value)
        title = title[0].upper() + title[1:]
        subtopic = SUBTOPIC_CONFIG["Gaming"]["map"].get(game_value)
        return title, subtopic

    template = random.choice(TITLE_TEMPLATES[category])
    filled = {}
    for key in FILL:
        if "{" + key + "}" in template:
            filled[key] = random.choice(FILL[key])
    if "{n}" in template:
        filled["n"] = n

    # derive a subtopic if this category supports drilling down and the
    # template actually used the driving fill word
    subtopic = None
    cfg = SUBTOPIC_CONFIG.get(category)
    if cfg and cfg["fill_key"] in filled:
        subtopic = cfg["map"].get(filled[cfg["fill_key"]])

    result = template.format(**filled)
    result = result[0].upper() + result[1:]
    return result, subtopic


def generate_dataset(num_posts=400):
    posts = []
    categories = list(CATEGORIES.keys())
    weights = [CATEGORIES[c]["weight"] for c in categories]

    base_time = datetime(2026, 6, 1)

    for i in range(num_posts):
        category = random.choices(categories, weights=weights, k=1)[0]
        creator = random.choice(CATEGORIES[category]["creators"])
        title, subtopic = make_title(category, i)
        # engagement score correlated loosely with category weight (clickbait-y
        # categories skew higher) plus noise, clipped 0-100
        base_engagement = CATEGORIES[category]["weight"] * 2
        engagement_score = max(0, min(100, int(random.gauss(base_engagement + 20, 15))))
        timestamp = (base_time + timedelta(minutes=random.randint(0, 60 * 24 * 30))).isoformat()

        post = {
            "id": f"post_{i:04d}",
            "title": title,
            "category": category,
            "creator": creator,
            "engagement_score": engagement_score,
            "timestamp": timestamp,
        }
        if subtopic:
            post["subtopic"] = subtopic
        posts.append(post)

    return posts


if __name__ == "__main__":
    dataset = generate_dataset(900)
    with open("dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)

    # quick sanity summary
    from collections import Counter
    counts = Counter(p["category"] for p in dataset)
    print(f"Generated {len(dataset)} posts")
    print("Category distribution:")
    for cat, count in counts.most_common():
        print(f"  {cat:10s} {count:4d}  ({count/len(dataset)*100:.1f}%)")
