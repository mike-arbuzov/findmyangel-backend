import React from 'react';
import './ProfileModal.css';
import type { Profile } from '../types';

interface ProfileModalProps {
  profile: Profile;
  onClose: () => void;
}

const ProfileModal: React.FC<ProfileModalProps> = ({ profile, onClose }) => {
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

  // Normalize LinkedIn URL (remove trailing slash)
  const normalizedLinkedInUrl = profile.linkedin_url?.replace(/\/+$/, '') || '';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div className="modal-header">
          <div className="modal-avatar">
            {profile.avatar_url ? (
              <img 
                src={profile.avatar_url} 
                alt={profile.name || 'Profile'} 
                onError={(e) => {
                  // Fallback to initials if image fails to load
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const parent = target.parentElement;
                  if (parent) {
                    parent.textContent = getInitials(profile.name);
                  }
                }}
              />
            ) : (
              getInitials(profile.name)
            )}
          </div>
          <div className="modal-title">
            <h2>{profile.name || 'Unknown'}</h2>
            {personal.headline && <p className="modal-headline">{personal.headline}</p>}
          </div>
          {normalizedLinkedInUrl && (
            <a
              href={normalizedLinkedInUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="modal-linkedin-link"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
              </svg>
              View LinkedIn Profile
            </a>
          )}
        </div>

        <div className="modal-body">
          <div className="modal-section">
            <h3>Personal Information</h3>
            <div className="info-grid">
              {personal.location && (
                <div className="info-item">
                  <strong>Location:</strong>
                  <span>{personal.location}</span>
                </div>
              )}
              {personal.current_role && (
                <div className="info-item">
                  <strong>Current Role:</strong>
                  <span>{personal.current_role}</span>
                </div>
              )}
              {personal.company && (
                <div className="info-item">
                  <strong>Company:</strong>
                  <span>{personal.company}</span>
                </div>
              )}
            </div>

            {personal.summary && (
              <div className="summary-section">
                <strong>Summary:</strong>
                <p>{personal.summary}</p>
              </div>
            )}

            {personal.experience && personal.experience.length > 0 && (
              <div className="experience-section">
                <strong>Experience:</strong>
                <ul>
                  {personal.experience.map((exp, idx) => (
                    <li key={idx}>
                      <div className="exp-title">{exp.title || 'N/A'}</div>
                      {exp.company && <div className="exp-company">{exp.company}</div>}
                      {exp.duration && <div className="exp-duration">{exp.duration}</div>}
                      {exp.description && <div className="exp-description">{exp.description}</div>}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {personal.education && personal.education.length > 0 && (
              <div className="education-section">
                <strong>Education:</strong>
                <ul>
                  {personal.education.map((edu, idx) => (
                    <li key={idx}>
                      {edu.school && <div className="edu-school">{edu.school}</div>}
                      {edu.degree && <div className="edu-degree">{edu.degree}</div>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {investment.is_investor && (
            <div className="modal-section">
              <h3>Investment Profile</h3>
              <div className="info-grid">
                {investment.investment_role && (
                  <div className="info-item">
                    <strong>Investment Role:</strong>
                    <span>{investment.investment_role}</span>
                  </div>
                )}
                {investment.investment_focus && investment.investment_focus.length > 0 && (
                  <div className="info-item">
                    <strong>Investment Focus:</strong>
                    <span>{investment.investment_focus.join(', ')}</span>
                  </div>
                )}
                {investment.investment_stage && investment.investment_stage.length > 0 && (
                  <div className="info-item">
                    <strong>Investment Stage:</strong>
                    <span>{investment.investment_stage.join(', ')}</span>
                  </div>
                )}
              </div>

              {investment.sectors_of_interest && investment.sectors_of_interest.length > 0 && (
                <div className="sectors-section">
                  <strong>Sectors of Interest:</strong>
                  <div className="sectors-list">
                    {investment.sectors_of_interest.map((sector, idx) => (
                      <span key={idx} className="sector-badge">{sector}</span>
                    ))}
                  </div>
                </div>
              )}

              {investment.portfolio_companies && investment.portfolio_companies.length > 0 && (
                <div className="portfolio-section">
                  <strong>Portfolio Companies:</strong>
                  <ul>
                    {investment.portfolio_companies.map((company, idx) => (
                      <li key={idx}>{company}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileModal;

