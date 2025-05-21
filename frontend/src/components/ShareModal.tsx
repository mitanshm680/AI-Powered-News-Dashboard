import React, { useRef } from 'react';
import { X, Link, Twitter, Facebook } from 'lucide-react';
import { Article } from '../types';

interface ShareModalProps {
  article: Article | null;
  onClose: () => void;
}

const ShareModal: React.FC<ShareModalProps> = ({ article, onClose }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  if (!article) return null;

  const handleBackgroundClick = (e: React.MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  const shareUrl = article.fullArticleUrl;
  const shareTitle = article.title;

  const shareToTwitter = () => {
    window.open(
      `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareTitle)}`,
      '_blank'
    );
  };

  const shareToFacebook = () => {
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
      '_blank'
    );
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl);
    alert('Link copied to clipboard!');
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={handleBackgroundClick}
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-fade-in"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800">Share Article</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2 line-clamp-2">{article.title}</p>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <button
            onClick={shareToTwitter}
            className="flex flex-col items-center justify-center p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Twitter className="h-6 w-6 text-[#1DA1F2] mb-2" />
            <span className="text-xs">Twitter</span>
          </button>
          <button
            onClick={shareToFacebook}
            className="flex flex-col items-center justify-center p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Facebook className="h-6 w-6 text-[#4267B2] mb-2" />
            <span className="text-xs">Facebook</span>
          </button>
          <button
            onClick={copyToClipboard}
            className="flex flex-col items-center justify-center p-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Link className="h-6 w-6 text-gray-700 mb-2" />
            <span className="text-xs">Copy Link</span>
          </button>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2 px-4 bg-blue-900 text-white rounded-lg hover:bg-blue-800 transition-colors"
        >
          Done
        </button>
      </div>
    </div>
  );
};

export default ShareModal;