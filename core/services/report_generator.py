"""
Report Generation Service
Transforms raw commits into human-readable daily reports
"""
from typing import List, Dict
from datetime import datetime, date
from collections import defaultdict
import re
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate formatted reports from commits"""

    def __init__(self):
        self.action_verbs = {
            'fix': ['fixed', 'fix', 'resolve', 'resolved', 'patch', 'bugfix'],
            'feature': ['add', 'added', 'implement', 'implemented', 'create', 'created', 'feature'],
            'refactor': ['refactor', 'refactored', 'restructure', 'reorganize', 'optimize', 'optimized'],
            'improve': ['improve', 'improved', 'enhance', 'enhance', 'update', 'updated'],
            'test': ['test', 'tests', 'add test', 'add tests'],
            'docs': ['doc', 'docs', 'documentation', 'comment', 'readme'],
        }

    def generate_report(self, commits: List[Dict], developer_name: str, report_date: date) -> Dict:
        """
        Generate a formatted report from commits
        
        Args:
            commits: List of normalized commits
            developer_name: Developer's name
            report_date: Date of the report
            
        Returns:
            Dictionary with html and text versions of report
        """
        # Group commits by repository
        repo_groups = defaultdict(list)
        for commit in commits:
            repo_groups[commit['repository']].append(commit)

        # Classify and enhance commits
        categorized = self._categorize_commits(commits)

        # Generate HTML report
        html_content = self._generate_html_report(
            developer_name,
            report_date,
            categorized,
            repo_groups
        )

        # Generate text report
        text_content = self._generate_text_report(
            developer_name,
            report_date,
            categorized,
            repo_groups
        )

        return {
            'html': html_content,
            'text': text_content,
            'commit_count': len(commits),
            'repo_count': len(repo_groups),
        }

    def _categorize_commits(self, commits: List[Dict]) -> Dict[str, List[str]]:
        """Categorize commits by action type"""
        categorized = defaultdict(list)

        for commit in commits:
            message = commit['message']
            enhanced_message = self._enhance_message(message)
            category = self._classify_commit(message)
            categorized[category].append(enhanced_message)

        return dict(categorized)

    def _classify_commit(self, message: str) -> str:
        """Classify commit into a category"""
        message_lower = message.lower()

        for category, keywords in self.action_verbs.items():
            if any(keyword in message_lower for keyword in keywords):
                return category

        return 'general'

    def _enhance_message(self, message: str) -> str:
        """
        Enhance commit message for readability
        Remove common prefixes and capitalize properly
        """
        # Remove common prefixes
        prefixes = ['feat: ', 'fix: ', 'refactor: ', 'docs: ', 'test: ', 'chore: ', 'style: ']
        for prefix in prefixes:
            if message.lower().startswith(prefix):
                message = message[len(prefix):].strip()

        # Capitalize first letter if not already
        if message and message[0].islower():
            message = message[0].upper() + message[1:]

        return message

    def _generate_html_report(
        self,
        developer: str,
        report_date: date,
        categorized: Dict,
        repo_groups: Dict
    ) -> str:
        """Generate HTML formatted report"""
        date_str = report_date.strftime('%d %b %Y')
        total_commits = sum(len(msgs) for msgs in categorized.values())

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 20px; margin-bottom: 10px; font-size: 16px; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        .category {{ margin: 15px 0; }}
        .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ecf0f1; font-size: 12px; color: #7f8c8d; }}
        .stats {{ background: #ecf0f1; padding: 10px; border-radius: 5px; margin: 15px 0; }}
        .repo-list {{ font-size: 13px; color: #7f8c8d; }}
    </style>
</head>
<body>
    <h1>📊 Daily Work Report</h1>
    <p><strong>{developer}</strong> • {date_str}</p>
"""

        # Category sections
        category_labels = {
            'fix': '🐛 Bug Fixes',
            'feature': '✨ Features',
            'refactor': '♻️ Refactoring',
            'improve': '⚡ Improvements',
            'test': '🧪 Tests',
            'docs': '📚 Documentation',
            'general': '📝 Other Updates',
        }

        for category in ['fix', 'feature', 'refactor', 'improve', 'test', 'docs', 'general']:
            if category in categorized and categorized[category]:
                html += f"""
    <div class="category">
        <h2>{category_labels.get(category, category)}</h2>
        <ul>
"""
                for msg in categorized[category]:
                    html += f"            <li>{msg}</li>\n"

                html += """        </ul>
    </div>
"""

        # Statistics
        html += f"""
    <div class="stats">
        <strong>Summary:</strong><br>
        Total Commits: {total_commits}<br>
        Repositories: {', '.join(repo_groups.keys())}
    </div>

    <div class="footer">
        <p>Generated by ReportForMe • Automated Daily Report</p>
    </div>
</body>
</html>
"""
        return html

    def _generate_text_report(
        self,
        developer: str,
        report_date: date,
        categorized: Dict,
        repo_groups: Dict
    ) -> str:
        """Generate plain text formatted report"""
        date_str = report_date.strftime('%d %b %Y')
        total_commits = sum(len(msgs) for msgs in categorized.values())

        text = f"""
DAILY WORK REPORT — {date_str}
Developer: {developer}
{'=' * 60}

"""

        category_labels = {
            'fix': '🐛 BUG FIXES',
            'feature': '✨ FEATURES',
            'refactor': '♻️ REFACTORING',
            'improve': '⚡ IMPROVEMENTS',
            'test': '🧪 TESTS',
            'docs': '📚 DOCUMENTATION',
            'general': '📝 OTHER UPDATES',
        }

        for category in ['fix', 'feature', 'refactor', 'improve', 'test', 'docs', 'general']:
            if category in categorized and categorized[category]:
                text += f"\n{category_labels.get(category, category)}\n"
                text += "-" * 40 + "\n"
                for msg in categorized[category]:
                    text += f"• {msg}\n"

        text += f"""
{'=' * 60}
SUMMARY
Total Commits: {total_commits}
Repositories: {', '.join(repo_groups.keys())}

Generated by ReportForMe
"""
        return text
