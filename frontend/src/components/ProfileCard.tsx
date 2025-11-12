import React from 'react';
import './ProfileCard.css';
import type { Profile } from '../types';

interface ProfileCardProps {
  profile: Profile;
  onClick: () => void;
}

const ProfileCard: React.FC<ProfileCardProps> = ({ profile, onClick }) => {
  const personal = profile.personal_info || {};
  const investment = profile.investment_profile || {};

  const getInitials = (name: string | undefined): string => {
    if (!name) return '?';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const relevanceScore = profile.relevance_score ?? null;
  const scorePercentage = relevanceScore !== null ? Math.round(relevanceScore) : null;
  
  // Calculate circumference for circular progress (radius = 16, so circumference ≈ 100.5)
  const circumference = 2 * Math.PI * 16;
  const strokeDashoffset = circumference - (scorePercentage !== null ? (scorePercentage / 100) * circumference : 0);

  return (
    <div className="profile-card" onClick={onClick}>
      <div className="card-header">
        <div className="avatar">
          {getInitials(profile.name)}
        </div>
        <div className="card-title">
          <h3>{profile.name || 'Unknown'}</h3>
          {personal.headline && (
            <p className="headline">{personal.headline}</p>
          )}
        </div>
        {scorePercentage !== null && (
          <div className="relevance-indicator" title={`Relevance: ${scorePercentage}%`}>
            <svg className="relevance-circle" viewBox="0 0 36 36">
              <circle
                className="relevance-circle-bg"
                cx="18"
                cy="18"
                r="16"
                fill="none"
                stroke="#e0e0e0"
                strokeWidth="2"
              />
              <circle
                className="relevance-circle-fill"
                cx="18"
                cy="18"
                r="16"
                fill="none"
                stroke="#000000"
                strokeWidth="2"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                transform="rotate(-90 18 18)"
              />
            </svg>
            <span className="relevance-score">{scorePercentage}%</span>
          </div>
        )}
      </div>

      <div className="card-body">
        {personal.location && (
          <div className="card-info">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            <span>{personal.location}</span>
          </div>
        )}

        {personal.current_role && (
          <div className="card-info">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
            <span>
              {personal.current_role}
              {personal.company && <span className="company"> at {personal.company}</span>}
            </span>
          </div>
        )}

        {investment.is_investor && (
          <div className="investor-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              <path d="M2 17l10 5 10-5"></path>
              <path d="M2 12l10 5 10-5"></path>
            </svg>
            {investment.investment_role || 'Investor'}
          </div>
        )}

        {investment.sectors_of_interest && investment.sectors_of_interest.length > 0 && (
          <div className="sectors">
            {investment.sectors_of_interest.slice(0, 3).map((sector, idx) => (
              <span key={idx} className="sector-tag">{sector}</span>
            ))}
            {investment.sectors_of_interest.length > 3 && (
              <span className="sector-tag">+{investment.sectors_of_interest.length - 3}</span>
            )}
          </div>
        )}
      </div>

      {profile.linkedin_url && (
        <div className="card-footer">
          <a
            href={profile.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="linkedin-link"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
            </svg>
            View LinkedIn
          </a>
        </div>
      )}
    </div>
  );
};

export default ProfileCard;

