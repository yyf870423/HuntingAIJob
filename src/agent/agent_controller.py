from jd_parser.extractor import SkillExtractor
from matcher.vector_matcher import VectorMatcher
from datasource.loader import DataSourceManager
from tracker.tracker import CandidateTracker

class HuntingAgent:
    def __init__(self):
        self.extractor = SkillExtractor()
        self.matcher = VectorMatcher()
        self.datasource = DataSourceManager()
        self.tracker = CandidateTracker()

    def run_from_jd(self, jd_text_or_path):
        skills = self.extractor.extract(jd_text_or_path)
        print(f"提取技能: {skills}")

        matched_candidates = self.matcher.query_by_skills(skills)
        print(f"本地数据库匹配: {matched_candidates}")

        external_candidates = self.datasource.search_candidates(skills)
        print(f"多渠道检索: {external_candidates}")

        all_candidates = matched_candidates + external_candidates
        self.tracker.track(all_candidates)
