// React 타입 정의
declare module 'react' {
  import * as React from 'react';
  export = React;
  export as namespace React;
  
  export type ReactNode = any;
  export type FormEvent = any;
  export type KeyboardEvent = any;
  export type DependencyList = any[];
  
  export function useState<T>(initialState: T | (() => T)): [T, (value: T | ((prev: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: DependencyList): void;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: DependencyList): T;
  export function useRef<T = undefined>(initialValue?: T): { current: T };
  
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
    interface Element extends React.ReactElement<any, any> {}
    interface ElementClass extends React.Component<any> {}
  }
}

// Heroicons 타입 정의
declare module '@heroicons/react/24/outline' {
  export const MagnifyingGlassIcon: any;
  export const XMarkIcon: any;
  export const ClockIcon: any;
  export const ArrowTopRightOnSquareIcon: any;
  export const ExternalLinkIcon: any;
}

// 환경 변수 타입 정의
declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: 'development' | 'production' | 'test';
    NEXT_PUBLIC_API_URL: string;
    NEXT_PUBLIC_APP_NAME: string;
  }
}

// 글로벌 타입 확장
declare global {
  var process: NodeJS.Process;
}
