import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 text-center">
      <h1 className="max-w-2xl text-4xl font-semibold tracking-tight sm:text-5xl">
        AI-powered placement readiness, for every student on campus.
      </h1>
      <p className="max-w-xl text-muted-foreground">
        Resume scoring, semantic job matching, and adaptive skill assessment — built for
        Training &amp; Placement Officers and the students they support.
      </p>
      <div className="flex gap-3">
        <Button asChild size="lg">
          <Link href="/login">Sign in</Link>
        </Button>
        <Button asChild size="lg" variant="outline">
          <Link href="/register">Create an account</Link>
        </Button>
      </div>
    </main>
  );
}
