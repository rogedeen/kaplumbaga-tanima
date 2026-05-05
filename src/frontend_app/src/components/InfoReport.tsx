import React from 'react';

type Props = {
  logs?: string[];
};

export default function InfoReport({ logs = [] }: Props) {
  return (
    <div className="bg-gray-900 rounded-md p-4 text-gray-300">
      <h4 className="text-md font-medium mb-2">Processing Log</h4>
      <div className="text-sm space-y-1">
        {logs.length === 0 ? (
          <div className="text-gray-500">No processing info yet.</div>
        ) : (
          logs.map((l, i) => (
            <div key={i} className="text-xs text-gray-400">{l}</div>
          ))
        )}
      </div>
    </div>
  );
}
