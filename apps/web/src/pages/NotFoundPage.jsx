import { Link } from "react-router-dom";
import { Satellite, ArrowLeft, Sprout } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/authStore";

export default function NotFoundPage() {
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="text-center max-w-md animate-fade-in">
        <div className="mx-auto h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
          <Satellite className="h-12 w-12 text-muted-foreground" />
        </div>
        <h1 className="text-3xl font-bold text-foreground mb-3">Página no encontrada</h1>
        <p className="text-base text-muted-foreground mb-8">
          El satélite no detectó esta página. Es posible que haya sido reubicada o nunca existió.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button asChild>
            <Link to={isAuth ? "/dashboard" : "/"}>
              <ArrowLeft className="h-4 w-4" />
              {isAuth ? "Volver al dashboard" : "Volver al inicio"}
            </Link>
          </Button>
          {isAuth && (
            <Button asChild variant="outline">
              <Link to="/analizar">
                <Sprout className="h-4 w-4" />
                Analizar finca
              </Link>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
