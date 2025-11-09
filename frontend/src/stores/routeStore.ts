import { create } from 'zustand';

export interface Route {
  id: string;
  vessel_id: string;
  origin_port: string;
  destination_port: string;
  distance_nm: number;
  estimated_time_hours: number;
  fuel_cost: number;
  created_at: string;
}

export interface RouteStore {
  routes: Route[];
  selectedRoute: Route | null;
  setRoutes: (routes: Route[]) => void;
  addRoute: (route: Route) => void;
  selectRoute: (route: Route) => void;
  deleteRoute: (id: string) => void;
}

export const useRouteStore = create<RouteStore>((set) => ({
  routes: [],
  selectedRoute: null,
  setRoutes: (routes) => set({ routes }),
  addRoute: (route) => set((state) => ({ routes: [...state.routes, route] })),
  selectRoute: (route) => set({ selectedRoute: route }),
  deleteRoute: (id) => set((state) => ({ routes: state.routes.filter((r) => r.id !== id) })),
}));
