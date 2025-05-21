/**
 * Formats a date string to a relative time format (e.g., "2h ago", "3d ago")
 */
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  
  // Handle future dates
  if (date > now) {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }
  
  const diffInMs = now.getTime() - date.getTime();
  
  // Convert to seconds
  const diffInSec = Math.floor(diffInMs / 1000);
  
  if (diffInSec < 60) {
    return `${diffInSec}s ago`;
  }
  
  // Convert to minutes
  const diffInMin = Math.floor(diffInSec / 60);
  
  if (diffInMin < 60) {
    return `${diffInMin}m ago`;
  }
  
  // Convert to hours
  const diffInHour = Math.floor(diffInMin / 60);
  
  if (diffInHour < 24) {
    return `${diffInHour}h ago`;
  }
  
  // Convert to days
  const diffInDay = Math.floor(diffInHour / 24);
  
  if (diffInDay < 7) {
    return `${diffInDay}d ago`;
  }
  
  // For older dates, show the actual date
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};