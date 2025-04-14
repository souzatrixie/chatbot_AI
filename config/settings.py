import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

settings = {
    "DB_CONNECTION": "mysql+pymysql://user:password@localhost:3306/database_name",
    "FAISS_INDEX_PATH": "faiss_index_file",
    "paths": {
        "avatar_url": "https://api.dicebear.com/9.x/adventurer/svg?size=64&backgroundColor=ffffff&eyes=variant19&glasses=variant04&hair=long09&hairColor=cb6820&skinColor=f2d3b1&mouth=variant25&hairProbability=100",
        "logo_path": os.path.join(BASE_DIR, "../interface/img/TE_logo.png"),
        "style_path": os.path.join(BASE_DIR, "../interface/style.css"),
        "user_path": os.path.join(BASE_DIR, "../interface/img/user.png")
    }
}
